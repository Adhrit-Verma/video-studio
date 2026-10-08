"""Re-arrange a track on its measured beat grid: make it longer (or shorter, or reordered)
by joining whole sections at downbeats, so a story can have its calm stretches and drops
where it needs them.

    python arrange_music.py [--config video.json] [--sync out/sync.json]
      -> public/<track>_arranged.wav
      -> out/sync.json rewritten for the arrangement (offset 0, kicks remapped);
         the measured source grid is kept as out/sync-source.json

video.json "arrangement": [[from, to], ...] in SOURCE beats (the grid analyze_music.py
measured, beat 0 = its offset). Sections play in order; the output beat count is the sum
of their lengths, so set totalBeats to it (the script prints it).

Rules learned the hard way:
- Join only on bar lines (multiples of 4 beats from a phrase start), never mid-bar: a
  join off the bar reads as a skip even when it lands on a beat.
- An equal-power crossfade of ~30 ms centred on the join hides the seam without
  smearing the downbeat transient that follows it.
- Reusing a section is fine; reusing the same 8 bars back to back sounds looped.
  Alternate energy (calm, build, full) the way the story alternates.
Run it before master_audio.py (which then masters the arrangement like any track).
Needs numpy and ffmpeg.
"""
import sys
import argparse
import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 44100
XF = 0.030


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="video.json")
    ap.add_argument("--sync", default="out/sync.json")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    sections = cfg["arrangement"]
    sync_path = Path(a.sync)
    src_path = Path("out/sync-source.json")
    if not src_path.exists():                      # keep the measured source grid once
        shutil.copy(sync_path, src_path)
    p = json.loads(src_path.read_text())
    beat = 60 / p["bpm"]
    x = load(Path("public") / p["music"])
    xf = int(XF * SR)
    out = np.zeros((0, 2))
    kicks, weights, pos = [], [], 0.0
    for i, (b0, b1) in enumerate(sections):
        if (b1 - b0) % 4:
            print(f"! section {i} [{b0}, {b1}] is not whole bars")
        s0 = int(round((p["offset"] + b0 * beat) * SR)) - xf // 2
        s1 = int(round((p["offset"] + b1 * beat) * SR)) + xf // 2
        seg = x[max(0, s0):s1].copy()
        if len(seg) < s1 - s0:
            seg = np.vstack([seg, np.zeros((s1 - s0 - len(seg), 2))])
        if len(out):
            ramp = np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
            out[-xf:] = out[-xf:] * ramp[::-1] + seg[:xf] * ramp
            out = np.vstack([out, seg[xf:]])
        else:
            out = seg[xf // 2:]                    # the first section starts on its downbeat
        for k, w in zip(p.get("kicks", []), p.get("kickWeights", [])):
            kb = k / beat                          # source kicks are video seconds from the offset
            if b0 <= kb < b1:
                kicks.append(round((pos + kb - b0) * beat, 3))
                weights.append(w)
        pos += b1 - b0
    total = pos
    n = int(round(total * beat * SR))
    out = out[:n] if len(out) >= n else np.vstack([out, np.zeros((n - len(out), 2))])
    track = Path("public") / f"{Path(p['music']).stem}_arranged.wav"
    peak = max(1e-9, np.abs(out).max())
    with wave.open(str(track), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(out / peak * 0.95, -1, 1) * 32767).astype("<i2").tobytes())
    sync = dict(p, music=track.name, offset=0, kicks=kicks, kickWeights=weights, arranged=True)
    sync_path.write_text(json.dumps(sync))
    print(f"{track}: {len(sections)} sections · {total:g} beats · {total * beat:.1f}s · {len(kicks)} kicks")
    print(f"-> set video.json totalBeats to {total:g}, then run master_audio.py")


if __name__ == "__main__":
    main()
