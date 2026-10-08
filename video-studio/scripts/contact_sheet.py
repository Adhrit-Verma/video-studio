"""Render stills at chosen beats (one bundle, fast) and tile them into a labelled sheet.

    python contact_sheet.py --comp Film --beats 3.5,10.5,19.5,28.5
    python contact_sheet.py --comp FilmTall --every 8 --safe reels

--beats: beat positions; pick one per scene, a little AFTER its entrances start
         (an element fading in exactly on beat n is invisible at frame n).
--every N: one still every N beats.
--safe reels|tiktok|shorts: outline the areas those apps cover (tall formats only).
Run from the video project (uses its tools/stills.mjs). Needs Pillow and Node.
Look at the sheet before every full render: stills cost seconds, renders cost minutes.
"""
import sys
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Covered areas on a 1080x1920 frame: (bottom px, right px, top px). Approximate; app UIs change.
SAFE = {"reels": (420, 130, 220), "tiktok": (480, 140, 160), "shorts": (400, 120, 180)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comp", default="Film")
    ap.add_argument("--beats", default="")
    ap.add_argument("--every", type=float, default=0)
    ap.add_argument("--props", default="out/props.json")
    ap.add_argument("--config", default="video.json")
    ap.add_argument("--safe", default="none", choices=["none", *SAFE])
    ap.add_argument("--cols", type=int, default=0)
    ap.add_argument("--out", default="out/sheet.jpg")
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    props = Path(a.props)
    bpm = json.loads(props.read_text())["bpm"] if props.exists() else cfg["bpm"]
    fpb = cfg["fps"] * 60 / bpm
    if a.beats:
        beats = [float(x) for x in a.beats.split(",")]
    else:
        step = a.every or 8
        beats = [step / 2 + i * step for i in range(int(cfg["totalBeats"] // step))]
    frames = [int(round(b * fpb)) for b in beats]
    cmd = f'node tools/stills.mjs --comp {a.comp} --frames {",".join(map(str, frames))} --outdir out/stills'
    if props.exists():
        cmd += f' --props "{props}"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        err = [l for l in (r.stdout + r.stderr).splitlines() if "Error" in l or "error:" in l]
        print("\n".join(err[:6]) or (r.stdout[-1500:] + r.stderr[-1500:]))
        raise SystemExit("stills failed")
    issues = sorted({l.strip() for l in r.stdout.splitlines() if "[layout]" in l or "[readability]" in l})
    for l in issues:
        print(l)
    shots = [(b, Path(f"out/stills/{a.comp}_{f:05d}.png")) for b, f in zip(beats, frames)]
    im0 = Image.open(shots[0][1])
    tall = im0.height > im0.width
    tw = 300 if tall else 480
    th = round(tw * im0.height / im0.width)
    cols = a.cols or (6 if tall else 3)
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 26)), "#222")
    d = ImageDraw.Draw(sheet)
    for i, (bt, png) in enumerate(shots):
        im = Image.open(png).convert("RGB").resize((tw, th))
        if a.safe != "none" and tall:
            bot, right, top = (v * th / 1920 for v in SAFE[a.safe])
            dd = ImageDraw.Draw(im)
            dd.rectangle([0, th - bot, tw - 1, th - 1], outline="#ff3b30", width=2)
            dd.rectangle([tw - right, th * 0.45, tw - 1, th - bot], outline="#ff3b30", width=2)
            dd.rectangle([0, 0, tw - 1, top], outline="#ff9500", width=2)
        x, y = (i % cols) * tw, (i // cols) * (th + 26)
        sheet.paste(im, (x, y + 26))
        d.text((x + 8, y + 6), f"beat {bt:g}  ({bt * 60 / bpm:.1f}s)", fill="#ddd")
    sheet.save(a.out, quality=88)
    print(f"{len(shots)} stills -> {a.out}" + (f" · {len(issues)} layout/readability warnings above" if issues else " · layout check clean"))


if __name__ == "__main__":
    main()
