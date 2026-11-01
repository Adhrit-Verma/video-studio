"""Vocal onsets (note/syllable starts) of a wav, for snapping lyric words to what's actually sung.

python onsets.py <vocal.wav> [out.json]
Spectral flux in the 150-5000 Hz band, adaptive threshold, peaks >= 0.12 s apart. Prints times (s).
"""
import json, subprocess, sys
import numpy as np

SR, N, HOP = 22050, 1024, 256
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.float32)
frames = np.lib.stride_tricks.sliding_window_view(x, N)[::HOP] * np.hanning(N)
mag = np.log1p(30 * np.abs(np.fft.rfft(frames, axis=1)))
f = np.fft.rfftfreq(N, 1 / SR)
band = mag[:, (f > 150) & (f < 5000)]
flux = np.maximum(np.diff(band, axis=0), 0).sum(axis=1)
flux = np.convolve(flux, np.hanning(5) / 2.5, "same")
thr = np.convolve(flux, np.ones(43) / 43, "same") * 1.05 + flux.mean() * 0.05    # ~0.5 s local mean
gap = int(0.1 * SR / HOP)
peaks, last = [], -gap
for i in range(1, len(flux) - 1):
    if flux[i] > thr[i] and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1] and i - last >= gap:
        peaks.append(round((i + 1) * HOP / SR, 3)); last = i
strength = {p: float(flux[int(p * SR / HOP) - 1] / flux.max()) for p in peaks}
print(" ".join(f"{p:.2f}" for p in peaks))
if len(sys.argv) > 2:
    json.dump([[p, round(strength[p], 3)] for p in peaks], open(sys.argv[2], "w"))
