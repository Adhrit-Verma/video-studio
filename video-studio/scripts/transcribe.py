"""Word-timed transcript of a voice note: python transcribe.py <audio> <out.json> [lang=hi]
Needs faster-whisper (pip install -r requirements-voice.txt; Python 3.10-3.12). Decodes with ffmpeg (faster-whisper's PyAV path breaks on some Windows setups)."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else "hi"
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
try:
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
except Exception:
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = model.transcribe(np.frombuffer(pcm, np.float32), language=lang, word_timestamps=True, beam_size=5)
data = {"language": info.language, "segments": []}
for s in segs:
    data["segments"].append({"start": s.start, "end": s.end, "text": s.text.strip(),
                             "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
    print(" ".join(f"{w.word.strip()}@{w.start:.2f}" for w in s.words))
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
