"""<reel>/captions.txt (original-recording times) + <reel>/audio/timemap.json -> <reel>/video/src/captions.json (edited times).

python build_captions.py <reel-dir>
captions.txt lines: "CH name t" (chapter start), "EN t: text" (English sub), or a chunk "t word | t word ..."."""
import json, pathlib, subprocess, sys

here = pathlib.Path(sys.argv[1])
tmap = json.load(open(here / "audio/timemap.json"))

def remap(t):
    for a, b, n in tmap:
        if t < a:                     # inside a removed pause: snap to the next kept segment
            return round(n, 3)
        if t <= b:
            return round(n + t - a, 3)
    return round(tmap[-1][2] + tmap[-1][1] - tmap[-1][0], 3)

chapters, chunks, subs = {}, [], []
for line in (here / "captions.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("CH "):
        _, name, t = line.split()
        chapters[name] = remap(float(t))
        continue
    if line.startswith("EN "):
        t, text = line[3:].split(": ", 1)
        subs.append({"t": remap(float(t)), "text": text})
        continue
    words = []
    for pair in line.split(" | "):
        t, w = pair.split(" ", 1)
        words.append({"t": remap(float(t)), "w": w})
    chunks.append({"t": words[0]["t"], "words": words})

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(here / "audio/voice.wav")], capture_output=True, text=True).stdout)
for i, c in enumerate(chunks):
    last = c["words"][-1]["t"]
    nxt = chunks[i + 1]["t"] if i + 1 < len(chunks) else dur
    c["end"] = round(min(nxt, last + 1.4), 3)
for i, s in enumerate(subs):
    s["end"] = subs[i + 1]["t"] if i + 1 < len(subs) else round(dur, 3)

out = {"dur": round(dur, 3), "chapters": chapters, "chunks": chunks, "subs": subs}
assert all(a["t"] <= b["t"] for a, b in zip(chunks, chunks[1:])), "chunks out of order"
json.dump(out, open(here / "video/src/captions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"{len(chunks)} chunks, {len(subs)} subs, {dur:.2f}s", out["chapters"])
