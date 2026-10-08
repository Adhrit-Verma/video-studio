"""Verify, on the RENDERED file, that the music sits where the video expects it.

    python verify_sync.py out/film.mp4 [--props out/props.json] [--config video.json] [--tolerance 20]

Two measurements:
1. Render offset (exact, any music): cross-correlates the rendered audio with the master
   WAV the video plays (props.music). Encoders shift audio (AAC priming, ~42 ms with
   Remotion 4); master_audio.py pre-shifts the cut by video.json "nudge". Net offset =
   measured shift - nudge. |net| <= tolerance passes; otherwise set nudge to the
   measured shift and re-run master_audio.py.
2. Grid check (music with kicks): for each expected kick (props.kicks) find the nearest
   onset in the same 30-120 Hz band analyze_music.py used (so detector bias cancels) and
   report median, spread (IQR) and drift across the film. Drift means a wrong tempo
   (re-run analyze_music.py); a wide spread means the grid doesn't match the music.
   Synthetic beats (gen_beat.py, props "generated": true) are exact by construction;
   their grid check is informational and never fails the verdict (a pitch-swept kick
   under an 808 detects loosely, and sound effects add onsets of their own).
±20 ms is below what viewers notice; well-synced cuts measured -6 ms median, 12 ms IQR.
Needs numpy and ffmpeg.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 22050
HOP = round(0.005 * SR) / SR   # exactly one analysis step in seconds (110 samples at 22050 Hz); 0.005 flat stretched every time by 0.23%


def decode(path, seconds=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR)]
    if seconds:
        cmd += ["-t", str(seconds)]
    raw = subprocess.run(cmd + ["-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def envelope(x, ms=1):
    h = int(SR * ms / 1000)
    n = len(x) // h * h
    return np.sqrt(np.add.reduceat(x[:n] ** 2, np.arange(0, n, h)) / h)


def render_lag_ms(rendered, master, max_ms=300):
    """Lag (ms) of rendered vs master: positive = the rendered audio is later."""
    a, b = envelope(rendered), envelope(master)
    n = min(len(a), len(b), 20000)                     # first 20 s at 1 ms resolution
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    lags = np.arange(-max_ms, max_ms + 1)
    sc = [np.dot(a[max(0, L):n + min(0, L)], b[max(0, -L):n - max(0, L)]) for L in lags]
    return int(lags[int(np.argmax(sc))])


def onsets(x):
    h = round(HOP * SR)
    n = len(x) // h * h
    e = np.add.reduceat(x[:n] ** 2, np.arange(0, n, h))
    e = np.convolve(e, np.ones(3) / 3, "same")
    return np.maximum(0, np.diff(np.log(e + 1e-9), prepend=0))


def kick_band(x):
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f[(fr < 30) | (fr > 120)] = 0                      # the band analyze_music.py uses
    return np.fft.irfft(f, len(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--props", default="out/props.json")
    ap.add_argument("--config", default="video.json")
    ap.add_argument("--tolerance", type=float, default=20, help="ms")
    a = ap.parse_args()
    props = json.loads(Path(a.props).read_text())
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8")) if Path(a.config).exists() else {}
    nudge_ms = 1000 * cfg.get("nudge", 0)
    x = decode(a.video)
    ok = True

    master = Path("public") / props["music"] if props.get("music") else None
    if master and master.exists() and props.get("offset", 0) == 0:
        lag = render_lag_ms(x, decode(master, 25))
        net = lag - nudge_ms
        print(f"render offset: rendered audio is {lag:+d} ms vs the master; nudge {nudge_ms:+.0f} ms "
              f"-> net {net:+.0f} ms vs the timeline")
        if abs(net) > a.tolerance:
            ok = False
            print(f"  fix: set video.json nudge to {lag / 1000:.3f}, re-run master_audio.py, re-render")
    else:
        print("render offset: skipped (no mastered music with offset 0 in props)")

    kicks = [k for k in props.get("kicks", []) if 0.1 < k < len(x) / SR - 0.1]
    if kicks:
        o = onsets(kick_band(x))
        thr = max(np.percentile(o[o > 0], 90) if (o > 0).any() else 0, 1e-6)
        w = int(0.08 / HOP)
        offs = []
        for k in kicks:
            i = int(k / HOP)
            seg = o[max(0, i - w):i + w + 1]
            if seg.size and seg.max() > thr:
                offs.append(((max(0, i - w) + int(np.argmax(seg))) * HOP - k) * 1000)
        offs = np.array(offs)
        if len(offs) < 3:
            print(f"grid check: only {len(offs)}/{len(kicks)} kicks found; check the music/props pairing")
        else:
            med = float(np.median(offs))
            iqr = float(np.percentile(offs, 75) - np.percentile(offs, 25))
            line = f"grid check: {len(offs)}/{len(kicks)} kicks · median {med:+.0f} ms · IQR {iqr:.0f} ms"
            if len(offs) >= 24:
                q = [float(np.median(c)) for c in np.array_split(offs, 4)]
                drift = max(q) - min(q)
                line += f" · per quarter {' '.join(f'{m:+.0f}' for m in q)} (drift {drift:.0f} ms)"
                if drift > 2 * a.tolerance and (props.get("generated") or props.get("arranged")):
                    line += ("\n  (informational: " + ("a generated beat is on the grid by construction" if props.get("generated")
                             else "an arranged track reorders passages, and the detector's bias differs per passage") +
                             "; the render offset above is the exact check)")
                elif drift > 2 * a.tolerance:
                    ok = False
                    line += "\n  drift: the tempo is wrong; re-run analyze_music.py"
            else:
                line += " · too few kicks to judge drift"
            print(line)

    print("-> IN SYNC" if ok else "-> OFF")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
