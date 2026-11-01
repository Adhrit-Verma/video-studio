"""Forced-align known (romanized) lyrics to a vocal with torchaudio's MMS_FA. Far tighter than Whisper on singing.

python align.py <audio> <start_s> <lyrics.txt> <out.json> [film_offset]
<audio> from <start_s> on is aligned; lyrics.txt = rows of "time word | time word" (times ignored, words used),
blank row = new couplet. Output: {"lines": [[{"w","t","e"}...]...]} with times = audio time - film_offset.
"""
import json, re, subprocess, sys
import numpy as np
import torch
from torchaudio.pipelines import MMS_FA as bundle

src, start, lyr, out = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
offset = float(sys.argv[5]) if len(sys.argv) > 5 else start
SR = bundle.sample_rate
pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", src, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
wave = torch.from_numpy(np.frombuffer(pcm, np.float32).copy())[None]

lines = []
for row in open(lyr, encoding="utf-8"):
    row = row.strip()
    if row and not row.startswith("#"):
        lines.append([p.split(" ", 1)[1] for p in row.split(" | ")])
words = [w for l in lines for w in l]
norm = [re.sub(r"[^a-z']", "", w.lower()).replace("'", "") for w in words]

model, tok, aligner = bundle.get_model(), bundle.get_tokenizer(), bundle.get_aligner()
with torch.inference_mode():
    emission, _ = model(wave)
    spans = aligner(emission[0], tok(norm))
fps = wave.shape[1] / emission.shape[1] / SR            # seconds per emission frame
res, i = [], 0
for l in lines:
    row = []
    for w in l:
        s = spans[i]
        row.append({"w": w, "t": round(start + s[0].start * fps - offset, 3), "e": round(start + s[-1].end * fps - offset, 3)})
        i += 1
    res.append(row)
    print(" ".join(f"{x['w']}@{x['t']:.2f}-{x['e']:.2f}" for x in row))
json.dump({"lines": res}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
