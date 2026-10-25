"""Shortlist the usable moments in phone clips and photos, so a film is cut by eye, not by rotation.

    python clip_moments.py <folder or files...> [--out out/moments] [--step 0.25] [--top 8]
      -> <out>/moments.json   per clip: ranked moments (start, end, peak, score, tags) and rejected stretches;
                              per photo: score, flags, duplicates
      -> <out>/moments.md     the same as tables
      -> <out>/<clip>.jpg     contact sheet of the clip's top moments, numbered, with times and tags
      -> <out>/photos.jpg     every photo, numbered; duplicates and weak ones marked

The signals are cheap (numpy + Pillow + ffmpeg): sharpness (Laplacian variance, relative to the clip),
steadiness (frame difference), exposure, and skin coverage in the centre of the frame (a rough
"a person is in frame" cue). They SHORTLIST. Look at the sheets to choose: expressions, eye contact
and meaning need eyes (references/editing.md §2-3).
Tags: hold = sharp, steady, person in frame (tender holds, slow motion); action = a motion peak that
is still sharp (cut on it). Flags: blur / soft, dark, blown, legs? (skin only low in the frame: legs or
hands with no face), no-face? (floors, ceilings, pockets; also far-away wide shots, so check).
With OpenCV installed (pip install opencv-python) a real face detector replaces the skin cue; without it,
close crops of hands can still pass. Either way, the sheets are the decision.
Rejected stretches never include soft-only samples.
"""
import argparse
import json
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:                                                # optional: real face detection when OpenCV is installed
    import cv2
    FACES = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
except Exception:
    FACES = None

VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}
PHOTO = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
W = 192                                            # analysis width (px)


def skin_share(c):
    y = 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]
    cb = 128 - 0.168736 * c[..., 0] - 0.331264 * c[..., 1] + 0.5 * c[..., 2]
    cr = 128 + 0.5 * c[..., 0] - 0.418688 * c[..., 1] - 0.081312 * c[..., 2]
    return float(((cb > 77) & (cb < 127) & (cr > 133) & (cr < 173) & (y > 40)).mean())


def stats(rgb):
    """sharpness, luminance, skin in the upper/lower frame, saturation, grey frame.
    Faces sit in the upper part of phone footage; skin only in the lower part is usually legs or hands."""
    a = rgb.astype(np.float32)
    g = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    h, w = g.shape
    up = skin_share(a[int(h * 0.05):int(h * 0.55), int(w * 0.15):int(w * 0.85)])
    low = skin_share(a[int(h * 0.55):, int(w * 0.1):int(w * 0.9)])
    sat = float((a.max(-1) - a.min(-1)).mean() / 255)
    st = {"sharp": float(lap.var()), "lum": float(g.mean() / 255), "skin": up, "skin_low": low, "sat": sat}
    if FACES is not None:
        big = cv2.resize(g.astype(np.uint8), (w * 2, h * 2))
        st["faces"] = int(len(FACES.detectMultiScale(big, 1.1, 4, minSize=(28, 28))))
    return st, g


def flags_for(sharp_rel, st):
    f = []
    if sharp_rel < 0.2: f.append("blur")
    elif sharp_rel < 0.35: f.append("soft")
    if st["lum"] < 0.12: f.append("dark")
    if st["lum"] > 0.9: f.append("blown")
    if "faces" in st:                                      # OpenCV available: trust the detector
        if st["faces"] == 0: f.append("no-face?")
    elif st["sat"] > 0.06:                                 # colour image: the skin cue means something
        if st["skin_low"] > 0.12 and st["skin"] < 0.04: f.append("legs?")
        elif st["skin"] < 0.015: f.append("no-face?")
    return f


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def frames(path, step):
    """yield rgb arrays sampled every `step` s at width W (rotation applied by ffmpeg)"""
    first = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1", "-vf", f"scale={W}:-2",
                            "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    w, h = Image.open(BytesIO(first)).size
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={1 / step},scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.wait()


def analyse_clip(path, step, top):
    rows, prev = [], None
    for i, rgb in enumerate(frames(path, step)):
        st, g = stats(rgb)
        motion = float(np.abs(g - prev).mean() / 255) if prev is not None else 0.0
        prev = g
        rows.append({"t": round(i * step, 2), **st, "motion": motion})
    if not rows: return None
    ref = np.percentile([r["sharp"] for r in rows], 90) or 1
    mot = np.array([r["motion"] for r in rows])
    for r in rows:
        r["sharp_rel"] = min(1.0, r["sharp"] / ref)
        r["flags"] = flags_for(r["sharp_rel"], r)
        person = (1.0 if r["faces"] else 0.2) if "faces" in r else min(1, r["skin"] / 0.2) if r["sat"] > 0.06 else 0.6
        r["score"] = (0.45 * r["sharp_rel"] + 0.30 * person
                      + 0.15 * (1 - min(1, r["motion"] / 0.08)) + 0.10 * (0.12 <= r["lum"] <= 0.9))
    good = [not (set(r["flags"]) - {"soft"}) and r["score"] >= max(0.45, np.percentile([x["score"] for x in rows], 50)) for r in rows]
    moments, i = [], 0
    while i < len(rows):                                   # runs of good samples, split at 3 s
        if not good[i]: i += 1; continue
        j = i
        while j + 1 < len(rows) and good[j + 1] and rows[j + 1]["t"] - rows[i]["t"] < 3: j += 1
        seg = rows[i:j + 1]
        pk = max(seg, key=lambda r: r["score"])
        tags = []
        if np.mean([r["motion"] for r in seg]) < 0.03 and np.mean([r["skin"] for r in seg]) > 0.08: tags.append("hold")
        moments.append({"start": seg[0]["t"], "end": round(seg[-1]["t"] + step, 2), "peak": pk["t"],
                        "score": round(float(np.mean([r["score"] for r in seg])), 3), "tags": tags})
        i = j + 1
    thr = np.percentile(mot, 70) if len(mot) > 3 else 1
    for k in range(1, len(rows) - 1):                      # action peaks: motion maxima that stay sharp
        r = rows[k]
        if r["motion"] > thr and r["motion"] >= rows[k - 1]["motion"] and r["motion"] >= rows[k + 1]["motion"] and r["sharp_rel"] >= 0.5:
            moments.append({"start": round(max(0, r["t"] - step), 2), "end": round(r["t"] + step, 2), "peak": r["t"],
                            "score": round(r["score"], 3), "tags": ["action"]})
    moments.sort(key=lambda m: -m["score"] * min(1.0, (m["end"] - m["start"]) / 1.5) ** 0.5)
    rejects, i = [], 0
    while i < len(rows):                                   # rejected stretches (merged)
        if not rows[i]["flags"]: i += 1; continue
        j = i
        while j + 1 < len(rows) and rows[j + 1]["flags"]: j += 1
        why = sorted({f for r in rows[i:j + 1] for f in r["flags"]})
        rejects.append({"start": rows[i]["t"], "end": round(rows[j]["t"] + step, 2), "why": why})
        i = j + 1
    return {"duration": round(probe(path), 2), "moments": moments[:top], "rejects": rejects}


def font(size):
    try: return ImageFont.load_default(size=size)
    except TypeError: return ImageFont.load_default()


def sheet_clip(path, res, out):
    tiles = []
    for k, m in enumerate(res["moments"], 1):
        png = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(m["peak"]), "-i", str(path), "-frames:v", "1",
                              "-vf", "scale=240:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        if not png: continue
        im = Image.open(BytesIO(png)).convert("RGB")
        lab = Image.new("RGB", (im.width, 44), "#111")
        d = ImageDraw.Draw(lab)
        d.text((6, 3), f"#{k} {m['start']:.2f}-{m['end']:.2f}s", fill="#fff", font=font(15))
        d.text((6, 23), f"{m['score']:.2f} {' '.join(m['tags'])}", fill="#ffcc66", font=font(14))
        t = Image.new("RGB", (im.width, im.height + 44)); t.paste(im, (0, 0)); t.paste(lab, (0, im.height))
        tiles.append(t)
    if not tiles: return
    cols = min(4, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    tw, th = max(t.width for t in tiles), max(t.height for t in tiles)
    s = Image.new("RGB", (cols * tw, rows * th), "#000")
    for k, t in enumerate(tiles): s.paste(t, ((k % cols) * tw, (k // cols) * th))
    s.save(out / f"{path.stem}.jpg", quality=88)


def ahash(img):
    g = np.asarray(img.convert("L").resize((9, 8)), np.int16)
    return (g[:, 1:] > g[:, :-1]).flatten()              # difference hash, 64 bits


def analyse_photos(paths, out):
    res, thumbs = [], []
    for k, p in enumerate(paths, 1):
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        small = im.copy(); small.thumbnail((W, W * 2))
        st, _ = stats(np.asarray(small))
        res.append({"n": k, "file": p.name, "size": list(im.size), **{k2: round(v, 3) for k2, v in st.items()}, "hash": ahash(im)})
        t = im.copy(); t.thumbnail((200, 300)); thumbs.append(t)
    ref = np.percentile([r["sharp"] for r in res], 90) or 1 if res else 1
    for r in res:
        r["flags"] = flags_for(min(1.0, r["sharp"] / ref), r)
        r["dup_of"] = next((q["n"] for q in res if q["n"] < r["n"] and int((q["hash"] != r["hash"]).sum()) <= 6), None)
    if res:
        cols = 6; rows = (len(res) + cols - 1) // cols
        s = Image.new("RGB", (cols * 210, rows * 340), "#000")
        for i, (r, t) in enumerate(zip(res, thumbs)):
            x, y = (i % cols) * 210 + 5, (i // cols) * 340 + 5
            s.paste(t, (x, y))
            note = (f"DUP of #{r['dup_of']} " if r["dup_of"] else "") + " ".join(r["flags"])
            d = ImageDraw.Draw(s)
            d.text((x, y + 302), f"#{r['n']} {r['file'][:22]}", fill="#fff", font=font(13))
            if note: d.text((x, y + 318), note, fill="#ff6b6b", font=font(13))
        s.save(out / "photos.jpg", quality=88)
    for r in res: del r["hash"]
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default="out/moments")
    ap.add_argument("--step", type=float, default=0.25)
    ap.add_argument("--top", type=int, default=8)
    a = ap.parse_args()
    files = []
    for i in a.inputs:
        p = Path(i)
        files += sorted(x for x in p.iterdir() if x.suffix.lower() in VIDEO | PHOTO) if p.is_dir() else [p]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    report = {"clips": {}, "photos": []}
    md = ["# Moments", "", "Shortlist only: look at the sheets before choosing (references/editing.md).", ""]
    for f in [x for x in files if x.suffix.lower() in VIDEO]:
        res = analyse_clip(f, a.step, a.top)
        if not res: continue
        report["clips"][f.name] = res
        sheet_clip(f, res, out)
        md += [f"## {f.name} ({res['duration']} s) → {f.stem}.jpg", "", "| # | in-out (s) | peak | score | tags |", "|---|---|---|---|---|"]
        md += [f"| {k} | {m['start']:.2f}-{m['end']:.2f} | {m['peak']:.2f} | {m['score']:.2f} | {' '.join(m['tags'])} |"
               for k, m in enumerate(res["moments"], 1)]
        if res["rejects"]:
            md += ["", "Avoid: " + "; ".join(f"{r['start']:.2f}-{r['end']:.2f} s ({', '.join(r['why'])})" for r in res["rejects"])]
        md.append("")
        print(f"{f.name}: {len(res['moments'])} moments, {len(res['rejects'])} rejected stretches")
    photos = [x for x in files if x.suffix.lower() in PHOTO]
    if photos:
        report["photos"] = analyse_photos(photos, out)
        md += ["## Photos → photos.jpg", "", "| # | file | flags | duplicate of |", "|---|---|---|---|"]
        md += [f"| {r['n']} | {r['file']} | {' '.join(r['flags'])} | {('#' + str(r['dup_of'])) if r['dup_of'] else ''} |" for r in report["photos"]]
        dups = sum(1 for r in report["photos"] if r["dup_of"])
        print(f"{len(photos)} photos, {dups} duplicates")
    (out / "moments.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (out / "moments.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"-> {out}/moments.md, contact sheets in {out}/")


if __name__ == "__main__":
    main()
