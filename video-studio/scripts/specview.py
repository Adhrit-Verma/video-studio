"""Spectrogram + loudness strip with lyric word marks, to check lyric sync by eye.

python specview.py <vocal.wav> <lyrics.json> <out.png> [start end]
Red ticks = word times in lyrics.json (film seconds). Rows of 6 s.
"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

SR, N, HOP, ROW, PX = 16000, 1024, 160, 6.0, 260          # 100 frames/s, 260 px per second
wav, ly, out = sys.argv[1:4]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.float32)
t0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
t1 = float(sys.argv[5]) if len(sys.argv) > 5 else len(x) / SR
fr = np.lib.stride_tricks.sliding_window_view(x, N)[::HOP] * np.hanning(N)
S = 20 * np.log10(np.abs(np.fft.rfft(fr, axis=1))[:, :int(4000 / (SR / N))].T + 1e-6)
S = np.clip((S - (S.max() - 70)) / 70, 0, 1)[::-1]
rms = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-6)
L = json.load(open(ly, encoding="utf-8"))
words = [w for c in L["couplets"] for l in c for w in l] if "couplets" in L else [w for l in L["lines"] for w in l]
rows = int(np.ceil((t1 - t0) / ROW))
H = S.shape[0] + 70
img = Image.new("RGB", (int(ROW * PX), rows * (H + 30)), "white")
d = ImageDraw.Draw(img)
for r in range(rows):
    a = t0 + r * ROW
    i0, i1 = int(a * 100), min(int(min(a + ROW, t1) * 100), len(rms))
    spec = (255 * (1 - S[:, i0:i1])).astype(np.uint8)
    im = Image.fromarray(spec).resize((int((i1 - i0) / 100 * PX), S.shape[0]))
    y = r * (H + 30)
    img.paste(im, (0, y))
    pts = [((i - i0) / 100 * PX, y + S.shape[0] + 60 - max(0, rms[i] + 60)) for i in range(i0, i1)]
    d.line(pts, fill=(0, 90, 200), width=2)
    for s in range(int(a), int(a + ROW) + 1):
        d.text(((s - a) * PX + 2, y + H + 2), f"{s}s", fill="black")
        d.line([((s - a) * PX, y), ((s - a) * PX, y + H)], fill=(200, 200, 200))
    for w in words:
        if a <= w["t"] < a + ROW:
            xx = (w["t"] - a) * PX
            d.line([(xx, y), (xx, y + H)], fill=(230, 0, 0), width=2)
            d.text((xx + 3, y + 3), w["w"], fill=(230, 0, 0))
img.save(out)
