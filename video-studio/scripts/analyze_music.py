"""Measure a track's real beat grid so the video cuts on it.

    python analyze_music.py public/song.mp3 --drop 15.5 --bpm 115 [--config video.json]
      -> out/sync.json  {music, bpm, offset, kicks, kickWeights}

--drop: roughly where the track's drop is (seconds, from your ears or a loudness
scan). It lands on video.json's dropBeat. --bpm: a rough tempo (tap it, or look it up).

How, and why this way (each rule cost a failed render to learn):
- The beat is where the KICKS are (30-120 Hz). Full-band hits are no good for
  the grid: in phonk/trap, snares and hats flip between on- and off-beat from
  section to section, and a fit over them drifts.
- Tempo = the period whose 8th-note grid all kick hits agree with (phase coherence),
  refined by least squares; works for kicks on every beat and for syncopated 3-3-2.
  A flat BPM guess (115 vs a real 115.54) drifts ~50 ms by the end: visibly late.
- Windows whose kicks sit on the off-beat (quiet outros) are outliers: drop the
  worst and refit until every window agrees within 40 ms.
- The "drop" is the grid beat nearest your mark, not the loudest transient: a
  pickup hit 65 ms early once made every cut early.
- Low-band energy must be smoothed before the log, or the onset curve is noise.
Needs numpy and ffmpeg on PATH.
"""
import sys
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 22050
HOP = round(0.005 * SR) / SR   # exactly one analysis step in seconds (110 samples at 22050 Hz); 0.005 flat stretched every time by 0.23%


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def band(x, lo, hi):
    f = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    f[(freqs < lo) | (freqs > hi)] = 0
    return np.fft.irfft(f, len(x))


def onsets(x):
    """Onset strength every HOP seconds (rise of log energy), ~10 ms tolerance."""
    h = round(HOP * SR)
    n = len(x) // h * h
    e = np.add.reduceat(x[:n] ** 2, np.arange(0, n, h))
    e = np.convolve(e, np.ones(3) / 3, "same")
    o = np.maximum(0, np.diff(np.log(e + 1e-9), prepend=0))
    return np.convolve(o, np.exp(-0.5 * (np.arange(-6, 7) / 2.5) ** 2), "same")


def peak_times(o, lo, hi, pct=97, gap=0.1):
    """Times and strengths of local onset maxima above the pct-th percentile."""
    i0, i1 = max(1, int(lo / HOP)), min(len(o) - 1, int(hi / HOP))
    seg = o[i0:i1]
    if len(seg) < 10:
        return np.array([]), np.array([])
    thr = np.percentile(seg, pct)
    w = max(1, int(gap / HOP))
    idx = [i for i in range(i0, i1) if o[i] > thr and o[i] == o[max(0, i - w):i + w + 1].max()]
    return np.array(idx) * HOP, o[idx]


def kick_grid(o, bpm, lo, hi):
    """Fit one tempo + phase to all kick hits at once, on the 8th-note grid.

    Kicks in syncopated genres (phonk, trap, reggaeton) sit on 8ths (3-3-2) rather than on
    every beat, so a per-window beat fit breaks; phase coherence of the hits against an
    8th grid does not. Scans +-8% around the rough tempo, then refines by least squares.
    """
    t, w = peak_times(o, lo, hi)
    if len(t) < 12:                                   # too little in that range: use the track
        t, w = peak_times(o, 0, len(o) * HOP)
    if len(t) < 8:
        raise SystemExit("not enough kick hits found; check --bpm or the track")
    rough = 60 / bpm
    best = (-1, rough, 0.0)
    for p in np.linspace(rough * 0.92, rough * 1.08, 3200):
        z = np.sum(w * np.exp(2j * np.pi * t / (p / 2))) / w.sum()
        if abs(z) > best[0]:
            best = (abs(z), p, (np.angle(z) / (2 * np.pi)) % 1 * (p / 2))
    coh, period, ph = best
    u = period / 2
    k = np.round((t - ph) / u)
    r = t - (ph + k * u)
    keep = np.abs(r) < u / 5                          # hits that are on the grid
    for tol in (u / 5, u / 8, 0.025):                 # refine, tightening: off-grid fills can't pull it
        if keep.sum() < 8:
            break
        u, ph = np.polyfit(k[keep], t[keep], 1)
        k = np.round((t - ph) / u)
        keep = np.abs(t - (ph + k * u)) < tol
    period = 2 * u
    r = t[keep] - (ph + k[keep] * u)
    worst = float(np.percentile(np.abs(r), 90))
    print(f"grid coherence {coh:.2f} (want > 0.4) · {int(keep.sum())}/{len(t)} hits on the 8th grid")
    return period, float(ph), worst, int(keep.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--drop", type=float, required=True, help="rough time of the drop, seconds")
    ap.add_argument("--bpm", type=float, required=True, help="rough tempo")
    ap.add_argument("--config", default="video.json")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    total, drop_beat = cfg["totalBeats"], cfg["dropBeat"]

    x = load(a.track)
    kick_o = onsets(band(x, 30, 120))
    full_o = onsets(x)
    rough = 60 / a.bpm
    lo = max(0.0, a.drop - drop_beat * rough - 2)
    hi = min(len(x) / SR, a.drop + (total - drop_beat) * rough + 2)
    period, anchor, worst, used = kick_grid(kick_o, a.bpm, lo, hi)
    drop = anchor + round((a.drop - anchor) / (period / 2)) * (period / 2)   # nearest 8th to your mark
    offset = drop - drop_beat * period
    end = offset + total * period
    if offset < 0:
        print(f"warning: the video would start {-offset:.2f}s before the track; lower dropBeat or pick a later drop")
    if end > len(x) / SR:
        print(f"warning: the video runs {end - len(x) / SR:.2f}s past the end of the track")

    # Accents for the visuals: 8th-note grid points with a real hit (kick band counts double).
    hits = []
    for g in np.arange(max(offset, 0), end, period / 2):
        i = int(g / HOP)
        if 4 <= i < len(kick_o) - 5:
            hits.append((round(g - offset, 3), float(2 * kick_o[i - 4:i + 5].max() + full_o[i - 4:i + 5].max())))
    vals = np.array([v for _, v in hits])
    cut, top = np.percentile(vals, 55), np.percentile(vals, 98)
    window = [(t, round(min(1.0, v / top), 2)) for t, v in hits if v >= cut]

    sync = {"music": Path(a.track).name, "bpm": round(60 / period, 4), "offset": round(offset, 4),
            "kicks": [t for t, _ in window], "kickWeights": [w for _, w in window]}
    Path("out").mkdir(exist_ok=True)
    Path("out/sync.json").write_text(json.dumps(sync))
    print(f"bpm {60 / period:.3f} · drop downbeat {drop:.3f}s · offset {offset:.3f}s")
    print(f"90% of grid hits within {worst * 1000:.0f} ms of the grid (want < 20)")
    print(f"{len(window)} accents -> out/sync.json")


if __name__ == "__main__":
    main()
