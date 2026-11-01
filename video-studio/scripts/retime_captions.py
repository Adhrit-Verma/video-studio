"""Re-time a reel's captions.txt with forced alignment (MMS_FA): word times + EN lines snap to the real speech.

python retime_captions.py <reel-dir>      (Python 3.12 with torch; reads <reel>/audio/raw-full.wav)
Rewrites captions.txt in place (keeps a captions.whisper.txt backup). CH lines are left alone.
"""
import pathlib, re, shutil, subprocess, sys
import numpy as np
import torch
from torchaudio.pipelines import MMS_FA as bundle

reel = pathlib.Path(sys.argv[1])
cap = reel / "captions.txt"
rows = cap.read_text(encoding="utf-8").splitlines()
is_chunk = lambda r: r.strip() and not r.startswith(("#", "CH ", "EN "))
chunks = [[p.split(" ", 1) for p in r.split(" | ")] for r in rows if is_chunk(r)]
words = [w for c in chunks for _, w in c]
norm = [re.sub(r"[^a-z]", "", w.lower()) or "a" for w in words]

SR = bundle.sample_rate
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(reel / "audio/raw-full.wav"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
wave = torch.from_numpy(np.frombuffer(pcm, np.float32).copy())[None]
model, tok, aligner = bundle.get_model(), bundle.get_tokenizer(), bundle.get_aligner()
with torch.inference_mode():
    emission, _ = model(wave)
    spans = aligner(emission[0], tok(norm))
fps = wave.shape[1] / emission.shape[1] / SR
times = iter([round(s[0].start * fps, 2) for s in spans])

out, i = [], 0
new_chunks = [" | ".join(f"{next(times):.2f} {w}" for _, w in c) for c in chunks]
for r in rows:
    if is_chunk(r):
        out.append(new_chunks[i]); i += 1
    else:
        out.append(r)
# each EN line starts with the chunk right after it
for k, r in enumerate(out):
    if r.startswith("EN "):
        nxt = next(x for x in out[k + 1:] if is_chunk(x))
        out[k] = f"EN {nxt.split(' ', 1)[0]}: {r.split(': ', 1)[1]}"
shutil.copy(cap, reel / "captions.whisper.txt")
cap.write_text("\n".join(out) + "\n", encoding="utf-8")
for old, new in zip([c[0][0] for c in chunks], [c.split(" ", 1)[0] for c in new_chunks]):
    print(f"{old:>6} -> {new:>6}  {'!' if abs(float(old) - float(new)) > 0.3 else ''}")
