"""Edit the user's own song to a target length smoothly: map it, pick joins, build the master.

Use this when a song is longer than the film and the user agreed to an edit (default is
to play their song uncut). Few joins, on bar lines, between passages that sound alike;
never reshuffle a favourite into a medley (that is what users reject).

    python edit_song.py song.mp3 --bpm 98 --map
        -> a bar table (energy, bass, brightness, gap-then-hit drops) + out/song-map.md
    python edit_song.py song.mp3 --bpm 98 --join 41:11 --join 20:43
        -> how seamless "end of bar 41 -> start of bar 11" would be (want >= 0.93)
    python edit_song.py song.mp3 --bpm 98 --segments 29-41,11-20,43- --beats 98
        -> public/<song>_edit.wav (mastered), out/props.json, out/sync.json, out/edit.md

How:
- Tempo/phase come from analyze_music.kick_grid (8th-note fit, any kick pattern).
- Bars: --phase (in 8ths) picks which grid point is a downbeat; default = the phase where
  the song's sections change (energy steps line up with bar lines). Check it in the map.
- A join's score compares what would naturally follow the out-bar with what you splice in
  (log spectra, 0..1). >= 0.95 is inaudible in practice; < 0.9 reads as a cut.
- Joins are 30 ms equal-power crossfades centred on the bar line; the first segment fades in
  over 0.25 s; a warm (low-passed) reverb tail follows the last note; master pre-shifted by
  video.json "nudge" and normalised to -14 LUFS / -1 dBTP.
- Kicks for the visuals are measured on the EDIT (not mapped from the source), weighted.
Needs numpy and ffmpeg.
"""
import argparse
import json
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import analyze_music as am  # noqa: E402
from master_audio import envelopes, load, loudnorm  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 44100
XF = 0.030


def grid(track, bpm):
    x = am.load(track)
    o = am.onsets(am.band(x, 30, 120))
    period, ph, worst, used = am.kick_grid(o, bpm, 0, len(x) / am.SR)
    return x, o, period, ph


def rms(sig, a, b, sr):
    a, b = max(0, int(a * sr)), min(len(sig), int(b * sr))
    return float(np.sqrt(np.mean(sig[a:b] ** 2))) if b > a else 0.0


def pick_phase(x, period, ph):
    """The 8th offset whose bar lines sit on the biggest energy changes (section edges)."""
    u, bar = period / 2, period * 4
    best = (-1, 0)
    for p in range(8):
        t0 = ph + p * u
        sc = [abs(np.log((rms(x, t, t + period * 2, am.SR) + 1e-6) / (rms(x, t - period * 2, t, am.SR) + 1e-6)))
              for t in np.arange(t0 + bar, len(x) / am.SR - bar, bar)]
        s = float(np.mean(sorted(sc)[-max(3, len(sc) // 6):]))      # the strongest edges only
        best = max(best, (s, p))
    return best[1]


def spec(x, a, d=0.6):
    s = x[int(a * am.SR):int((a + d) * am.SR)]
    if len(s) < 64:
        return None
    m = np.log1p(np.abs(np.fft.rfft(s * np.hanning(len(s))))[: len(s) // 6])
    return m / (np.linalg.norm(m) + 1e-9)


def join_score(x, bar_t, out_bar, in_bar):
    """Similarity of what follows out_bar naturally vs what we splice in (after and before)."""
    sc = []
    for off in (0, -0.6):
        a, b = spec(x, bar_t(out_bar + 1) + off), spec(x, bar_t(in_bar) + off)
        if a is not None and b is not None:
            sc.append(float(a @ b))
    return min(sc) if sc else 0.0


def song_map(x, bar_t, n_bars):
    lowx = am.band(x, 30, 150)
    hix = am.band(x, 4000, 10000)
    ref = [rms(x, 0, len(x) / am.SR, am.SR), rms(lowx, 0, len(x) / am.SR, am.SR), rms(hix, 0, len(x) / am.SR, am.SR)]
    rows = ["| bar | time | energy | bass | bright | note |", "|---|---|---|---|---|---|"]
    for k in range(-1, n_bars):
        a, b = bar_t(k), bar_t(k + 1)
        if b <= 0 or a >= len(x) / am.SR:
            continue
        e = rms(x, a, b, am.SR) / ref[0]
        # a drop = a real hush (>= 0.2 s near-silent) at the bar line, then a loud bar
        pre = [rms(x, t, t + 0.1, am.SR) for t in np.arange(a - 0.7, a + 0.15, 0.05)]
        loud = rms(x, a, b, am.SR)
        hush = sum(v < 0.45 * loud for v in pre) >= 4
        prev = rms(x, bar_t(k - 1), a, am.SR) / ref[0] if a > 0 else 0
        gap = hush and e > 0.9 and e - prev >= 0.08          # hush + a real step up = a drop
        note = "gap -> hit (a drop)" if gap else ("quiet" if e < 0.7 else "full" if e > 1.0 else "")
        rows.append(f"| {k} | {a:7.2f}s | {e:.2f} {'#' * int(e * 12)} | {rms(lowx, a, b, am.SR) / ref[1]:.2f} | "
                    f"{rms(hix, a, b, am.SR) / ref[2]:.2f} | {note} |")
    return "\n".join(rows)


def build(track, segs, bar_t, period, beats, nudge, fps, tail, out_path):
    x = load(track)
    h = int(XF / 2 * SR)
    out = np.zeros((0, 2))
    starts = []
    for a, z in segs:
        ia = int(round(a * SR))
        iz = len(x) if z is None else int(round(z * SR))
        seg = x[max(0, ia - h): iz + h].copy()
        starts.append(max(0, len(out) - h) / SR)
        if not len(out):
            seg = seg[min(h, ia):]
            fi = int(0.25 * SR)
            seg[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi))[:, None] ** 2
            out = seg
        else:
            n = 2 * h
            w = np.linspace(0, np.pi / 2, n)[:, None]
            out = np.vstack([out[:-n], out[-n:] * np.cos(w) + seg[:n] * np.sin(w), seg[n:]])
    total = beats * period if beats else len(out) / SR + tail
    N = int(round(total * SR)) + int(nudge * SR)
    y = np.zeros((N, 2))
    y[: min(N, len(out))] = out[:N]
    # warm reverb tail on the last segment: low-passed noise IR (no hiss)
    rng = np.random.default_rng(3)
    irn = int(3.0 * SR)
    f = np.fft.rfftfreq(irn, 1 / SR)
    i0 = int(starts[-1] * SR)
    last = y[i0:].copy()
    for c in range(2):
        ir = np.fft.irfft(np.fft.rfft(rng.standard_normal(irn)) / (1 + (f / 3500) ** 2), irn) * np.exp(-np.arange(irn) / SR / 0.9)
        ir /= np.sqrt(np.sum(ir ** 2))
        size = 1 << int(np.ceil(np.log2(len(last) + irn)))
        y[i0:, c] += 0.22 * np.fft.irfft(np.fft.rfft(last[:, c], size) * np.fft.rfft(ir, size), size)[: len(last)]
    fo = int(min(1.2, total / 4) * SR)
    y[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
    y = y[int(nudge * SR):][: int(round(total * SR))]

    Path("out").mkdir(exist_ok=True)
    pre = Path("out") / f"{out_path.stem}_raw.wav"
    with wave.open(str(pre), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    out_path.parent.mkdir(exist_ok=True)
    m = loudnorm(pre, out_path)

    # kicks measured on the edit, shifted by nudge to when they are heard
    xe = am.load(str(pre))
    o = am.onsets(am.band(xe, 30, 120))
    t, wts = am.peak_times(o, 0, len(xe) / am.SR, pct=96)
    top = np.percentile(wts, 95) if len(wts) else 1
    kicks = [round(float(v) + nudge, 3) for v in t]
    weights = [round(float(min(1.0, v / top)), 2) for v in wts]
    energy, bassv = envelopes(y.mean(axis=1), fps)
    props = {"music": out_path.name, "bpm": round(60 / period, 4), "offset": 0, "edited": True,
             "kicks": kicks, "kickWeights": weights, "energy": energy, "bass": bassv}
    Path("out/props.json").write_text(json.dumps(props))
    Path("out/sync.json").write_text(json.dumps({k: props[k] for k in ("music", "bpm", "offset", "kicks", "kickWeights", "edited")}))
    return starts, total, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--bpm", type=float, required=True, help="rough tempo")
    ap.add_argument("--phase", type=int, help="which 8th of the grid is a downbeat (0-7); default: auto")
    ap.add_argument("--map", action="store_true")
    ap.add_argument("--join", action="append", default=[], help="OUT:IN bars, e.g. 41:11")
    ap.add_argument("--segments", help="bar ranges, inclusive: 29-41,11-20,43-")
    ap.add_argument("--beats", type=float, help="film length in beats (default: the edit + a tail)")
    ap.add_argument("--config", default="video.json")
    ap.add_argument("--tail", type=float, default=1.3)
    ap.add_argument("--out", help="default public/<song>_edit.wav")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8")) if Path(a.config).exists() else {}

    x, o, period, ph = grid(a.track, a.bpm)
    phase = a.phase if a.phase is not None else pick_phase(x, period, ph)
    t0 = ph + phase * period / 2
    t0 -= np.floor(t0 / (period * 4)) * period * 4             # bar 0 = first full bar
    bar_t = lambda k: t0 + k * period * 4                         # noqa: E731
    n_bars = int((len(x) / am.SR - t0) / (period * 4)) + 1
    print(f"{60 / period:.3f} BPM · bar {period * 4:.4f}s · bar 0 at {t0:.3f}s (phase {phase}/8"
          f"{', auto' if a.phase is None else ''}) · {n_bars} bars")

    if a.map:
        table = song_map(x, bar_t, n_bars)
        Path("out").mkdir(exist_ok=True)
        Path("out/song-map.md").write_text(f"# {Path(a.track).name}\n\n{60 / period:.3f} BPM, bar 0 at {t0:.3f}s\n\n{table}\n", encoding="utf-8")
        print(table + "\n-> out/song-map.md")
    for j in a.join:
        ob, ib = (int(v) for v in j.split(":"))
        s = join_score(x, bar_t, ob, ib)
        print(f"join end of bar {ob} -> bar {ib}: {s:.3f} {'(seamless)' if s >= 0.95 else '(ok)' if s >= 0.93 else '(audible cut)'}")
    if a.segments:
        segs, bars = [], []
        for part in a.segments.split(","):
            lo, hi = part.split("-")
            segs.append((bar_t(int(lo)), None if hi == "" else bar_t(int(hi) + 1)))
            bars.append((int(lo), None if hi == "" else int(hi)))
        for (_, h1), (l2, _) in zip(bars, bars[1:]):
            s = join_score(x, bar_t, h1, l2)
            print(f"join {h1} -> {l2}: {s:.3f}{'  <- will sound like a cut; pick other bars' if s < 0.9 else ''}")
        out_path = Path(a.out) if a.out else Path("public") / f"{Path(a.track).stem.replace(' ', '_')}_edit.wav"
        starts, total, m = build(a.track, segs, bar_t, period, a.beats, cfg.get("nudge", 0.026), cfg.get("fps", 30), a.tail, out_path)
        B = period
        lines = [f"# Edit of {Path(a.track).name}", f"{60 / B:.3f} BPM · film {total:.2f}s = {total / B:.1f} beats", ""]
        for (lo, hi), s in zip(bars, starts):
            lines.append(f"- film {s:6.2f}s (beat {s / B:5.1f}) <- song bars {lo}-{'' if hi is None else hi}")
        lines.append(f"\nSet video.json bpm {60 / B:.3f}, totalBeats {total / B:.1f}; scene cuts on the film beats above.")
        Path("out/edit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines) + f"\n-> {out_path} (loudness in {m['input_i']} -> -14 LUFS), out/props.json, out/edit.md")


if __name__ == "__main__":
    main()
