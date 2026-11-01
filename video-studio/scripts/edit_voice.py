"""Tighten pauses in the raw voice note, then master it for a reel (no SFX, no music).

python edit_voice.py <in.m4a> <outdir> [long-pause-start ...]
Pauses starting at the given original times keep LONG_GAP instead of MAX_GAP.
Writes voice-edit.wav (cut), voice.wav (mastered, -14 LUFS / -1 dBTP) and timemap.json
(kept segments: [orig_start, orig_end, new_start]) so captions can be remapped.
"""
import json, subprocess, sys
import numpy as np

SR = 48000
MAX_GAP = 0.45          # longest pause kept
LONG_GAP = 0.75         # kept before the emotional turns (start times below, original timeline)
XF = 0.02               # crossfade at each cut

src, out = sys.argv[1], sys.argv[2]
LONG_AT = [float(a) for a in sys.argv[3:]]   # lost-myself-reel used 72.08 103.81
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.float32).copy()

log = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=n=-50dB:d=0.4", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(l.split("silence_start: ")[1]) for l in log.splitlines() if "silence_start" in l]
ends = [float(l.split("silence_end: ")[1].split()[0]) for l in log.splitlines() if "silence_end" in l]
sil = [(max(s, 0.0), e) for s, e in zip(starts, ends)]

dur = len(x) / SR
keep, t = [], 0.0
for s, e in sil:
    if s <= 0.6:                        # leading silence (or a click before it): keep a short lead-in
        t = max(e - 0.25, 0.0); continue
    if e >= dur - 0.01:                 # trailing silence: short tail
        keep.append((t, min(s + 0.6, dur))); t = dur; break
    gap = LONG_GAP if any(abs(s - a) < 0.3 for a in LONG_AT) else MAX_GAP
    if e - s > gap:
        keep.append((t, s + gap / 2)); t = e - gap / 2
if t < dur:
    keep.append((t, dur))

fade = int(XF * SR)
ramp = np.linspace(0, 1, fade, dtype=np.float32)
parts, tmap, n = [], [], 0.0
for a, b in keep:
    seg = x[int(a * SR):int(b * SR)].copy()
    seg[:fade] *= ramp; seg[-fade:] *= ramp[::-1]
    parts.append(seg); tmap.append([round(a, 4), round(b, 4), round(n, 4)])
    n += len(seg) / SR
y = np.concatenate(parts)

edit = f"{out}/voice-edit.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", edit],
               input=y.tobytes(), check=True)

import master_voice                             # de-hum, tone, de-ess, leveler, -14 LUFS / -1.5 dBTP
mastered, info = master_voice.master(y)
master_voice.write(mastered, f"{out}/voice.wav")
json.dump(tmap, open(f"{out}/timemap.json", "w"), indent=0)
print(f"{dur:.1f}s -> {n:.1f}s, {len(keep)} segments", info)
