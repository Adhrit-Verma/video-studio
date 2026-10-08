"""Cut and finish the music on the beat grid: the "smooth finish".

    python master_audio.py [--sync out/sync.json] [--config video.json]
      -> public/<track>_master.wav + out/props.json (music = master, offset 0,
         energy/bass = per-frame 0..1 envelopes for audio-reactive visuals)
      -> out/cues.md: the grid beats ranked by musical intensity (where big moments land)

From video.json:
  introBeats   fade in over a beat; muffled "through a wall", opening up by this beat (0 = off)
  breaks       [[a, b], ...]: dip and muffle, then slam back on b (a 5 ms ramp, no click)
  endBeat      the end card: a sub impact, then a low-pass sweep into a warm reverb tail
  totalBeats   the length
  nudge        seconds; compensates the AAC encoder delay so kicks land on frames (see below)
Loudness: -14 LUFS integrated, -1 dBTP (streaming norm), two-pass ffmpeg loudnorm.

Rules learned the hard way:
- One continuous filter over the whole cut, driven by cutoff/gain curves. Processing
  regions separately and splicing them back clicked at every seam.
- Warm the reverb (low-pass it); white-noise IRs add hiss above the track's band.
- nudge 0.026: Remotion's AAC output lands audio ~42 ms late (encoder priming) and the
  kick detector reads masters ~16 ms early; net +26 ms. Re-measure with verify_sync.py
  after the first render and adjust if the toolchain differs.
Needs numpy and ffmpeg on PATH.
"""
import sys
import argparse
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 44100


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)


def lowpass(x, cutoff):
    """Two cascaded one-pole low-passes with a per-sample cutoff (Hz)."""
    a = np.exp(-2 * np.pi * np.asarray(cutoff, dtype=float) / SR)
    y = np.empty_like(x)
    s1 = x[0].copy()
    s2 = x[0].copy()
    for i in range(len(x)):
        s1 = (1 - a[i]) * x[i] + a[i] * s1
        s2 = (1 - a[i]) * s1 + a[i] * s2
        y[i] = s2
    return y


def reverb(x, seconds=2.4, decay=0.7):
    rng = np.random.default_rng(3)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t / decay)
        ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        size = 1 << int(np.ceil(np.log2(len(x) + n)))
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], size) * np.fft.rfft(ir, size), size)[: len(x)]
    return out


def impact(seconds=2.2):
    t = np.arange(int(seconds * SR)) / SR
    f = 32 + 40 * np.exp(-t / 0.08)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7) * np.minimum(1, t / 0.008)
    return np.tanh(1.8 * s)[:, None] * np.array([[0.55, 0.55]])


def curve(n, pts):
    pts = sorted((min(max(int(x), 0), n - 1), v) for x, v in pts)
    xs, ys = zip(*pts)
    return np.interp(np.arange(n), xs, ys)


def loudnorm(src, dst):
    first = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                            "loudnorm=I=-14:TP=-1.0:LRA=9:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(re.findall(r"\{[^{}]*\}", first)[-1])
    af = (f"loudnorm=I=-14:TP=-1.0:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", str(SR), str(dst)], check=True)
    return m


def norm(v):
    """Per-track robust 0..1: divide by the 98th percentile, clamp."""
    hi = np.percentile(v, 98) or v.max() or 1.0
    return np.clip(v / hi, 0, 1)


def envelopes(mono, fps):
    """Per-video-frame loudness and bass (30-180 Hz), fast attack and ~150 ms release."""
    hop = SR / fps
    n = int(len(mono) / hop)
    spec = np.fft.rfft(mono)
    f = np.fft.rfftfreq(len(mono), 1 / SR)
    low = np.fft.irfft(spec * ((f >= 30) & (f <= 180)), len(mono))
    rel = np.exp(-1 / (0.15 * fps))
    out = []
    for sig in (mono, low):
        e = np.array([np.sqrt(np.mean(sig[int(i * hop):int((i + 1) * hop)] ** 2)) for i in range(n)])
        for i in range(1, n):
            e[i] = max(e[i], e[i - 1] * rel)
        out.append([round(float(x), 3) for x in norm(e)])
    return out


def cue_scores(mono, beat_s, total):
    """Score each grid beat: 0.45 onset + 0.25 local onset contrast + 0.20 rms + 0.10 bass."""
    nfft, hop = 2048, 512
    frames = np.lib.stride_tricks.sliding_window_view(np.pad(mono, (0, nfft)), nfft)[::hop]
    mag = np.abs(np.fft.rfft(frames * np.hanning(nfft), axis=1))
    freqs = np.fft.rfftfreq(nfft, 1 / SR)
    lm = np.log1p(mag)
    onset = norm(np.r_[0, np.maximum(0, np.diff(lm, axis=0)).sum(axis=1)])
    r = int(0.5 * SR / hop)
    contrast = norm(np.array([max(0, onset[i] - np.median(onset[max(0, i - r):i + r + 1])) for i in range(len(onset))]))
    rms = norm(np.sqrt((frames ** 2).mean(axis=1)))
    bass = norm(mag[:, (freqs >= 30) & (freqs <= 180)].mean(axis=1))
    score = 0.45 * onset + 0.25 * contrast + 0.20 * rms + 0.10 * bass
    w = max(1, int(0.04 * SR / hop))
    out = []
    for k in range(int(total)):
        i = int(round(k * beat_s * SR / hop))
        out.append(float(score[max(0, i - w):i + w + 1].max()) if i < len(score) else 0.0)
    return norm(np.array(out))


def write_cues(scores, beat_s, bpm, path):
    top = sorted(range(len(scores)), key=lambda k: -scores[k])[:10]
    lines = [f"# Music cues ({bpm:.2f} BPM, {len(scores)} beats)", "",
             "Strongest beats: put the 1-3 biggest moments (name reveal, payoff, logo) on these, near",
             "where the story wants them. Ignore a cue that would rush copy or break pacing.", "",
             "| beat | time | intensity |", "|---|---|---|"]
    lines += [f"| {k} | {k * beat_s:.2f}s | {scores[k]:.2f} |" for k in sorted(top)]
    lines += ["", "Every beat by bar (4 beats per bar; for sequential accents):", ""]
    lines += [f"- bar {b // 4 + 1} (beat {b}): " + " ".join(f"{s:.2f}" for s in scores[b:b + 4]) for b in range(0, len(scores), 4)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync", default="out/sync.json")
    ap.add_argument("--config", default="video.json")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    p = json.loads(Path(a.sync).read_text())
    track = Path("public") / p["music"]
    total = cfg["totalBeats"]
    end = cfg.get("endBeat", total - 6)
    intro = cfg.get("introBeats", 0)
    nudge = cfg.get("nudge", 0.026)
    beat = 60 / p["bpm"]
    b = lambda n: int(round(n * beat * SR))               # noqa: E731

    x = load(track)
    start = int(round((p["offset"] + nudge) * SR))
    n = b(total)
    y = x[max(0, start):max(0, start) + n].copy()
    if start < 0:
        y = np.vstack([np.zeros((-start, 2)), y])[:n]
    if len(y) < n:
        y = np.vstack([y, np.zeros((n - len(y), 2))])

    cut = [(0, 700 if intro else 18000)]
    if intro:
        cut += [(b(intro * 0.75), 2500), (b(intro), 18000)]
    gain = [(0, 1.0)]
    for s0, s1 in cfg.get("breaks", []):
        cut += [(b(s0) - 1, 18000), (b(s0 + 0.12), 450), (b(s1) - b(0.01), 900), (b(s1), 18000)]
        gain += [(b(s0) - 1, 1.0), (b(s0 + 0.12), 0.32), (b(s1) - b(0.01), 0.45), (b(s1), 1.0)]
    tail = total - end
    cut += [(b(end + tail * 0.3), 18000), (b(end + tail * 0.55), 5000), (b(total - 1), 700), (n - 1, 200)]
    gain += [(b(end + tail * 0.4), 1.0), (b(end + tail * 0.75), 0.6), (b(total - 1), 0.12), (n - 1, 0.0)]

    filtered = lowpass(y, curve(n, cut))
    y = filtered * curve(n, gain)[:, None]
    if intro:
        y[: b(1)] *= np.sin(np.linspace(0, np.pi / 2, b(1)))[:, None]
    s = b(end)
    k = n - s
    wash = lowpass(reverb(filtered[s:]), np.full(k, 7000.0))
    y[s:] += wash * curve(k, [(0, 0.2), (b(tail * 0.6), 0.4), (b(tail * 0.85), 0.55), (k - 1, 0.0)])[:, None]
    imp = impact()[:k]
    y[s:s + len(imp)] += imp
    y[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))[:, None]

    Path("out").mkdir(exist_ok=True)
    raw = Path("out") / f"{track.stem}_premaster.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y / max(1e-9, np.abs(y).max()) * 0.9, -1, 1) * 32767).astype("<i2").tobytes())
    master = Path("public") / f"{track.stem}_master.wav"
    m = loudnorm(raw, master)
    mono = load(master).mean(axis=1)
    energy, bass = envelopes(mono, cfg["fps"])
    write_cues(cue_scores(mono, beat, total), beat, p["bpm"], Path("out/cues.md"))
    props = dict(p, music=master.name, offset=0, energy=energy, bass=bass)
    Path("out/props.json").write_text(json.dumps(props))
    print(f"{master}: {n / SR:.2f}s · was {m['input_i']} LUFS / {m['input_tp']} dBTP -> -14 LUFS / -1 dBTP")
    print("-> out/props.json (with per-frame energy/bass), out/cues.md (strongest beats)")


if __name__ == "__main__":
    main()
