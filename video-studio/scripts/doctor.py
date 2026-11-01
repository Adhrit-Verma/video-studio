"""Check this machine for everything Video Studio needs, and say exactly what's missing.

    python doctor.py            core + optional parts, with the fix for each gap
    python doctor.py --strict   exit 1 if anything in the core is missing

Core (every video): Node 18+, npm/npx, ffmpeg + ffprobe on PATH, Python 3.10+ with numpy
and Pillow, and the skill reachable by Claude Code (~/.claude/skills/video-studio).
Optional: voice/lyric tools (faster-whisper, torch + torchaudio, Python <= 3.12), Blender
4.2+ for photoreal product shots, an NVIDIA GPU (Blender OptiX, faster Whisper).
"""
import importlib.util
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL = Path(__file__).resolve().parent.parent
WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"
rows = []


def run(*cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, shell=WIN)
        return (r.stdout + r.stderr).strip()
    except Exception:
        return ""


def check(part, name, ok, have, fix, core=True):
    rows.append((part, name, ok, have, fix, core))


def find_blender():
    exe = shutil.which("blender")
    if exe:
        return exe
    cands = []
    if WIN:
        for base in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("LOCALAPPDATA", "")):
            cands += sorted(Path(base, "Blender Foundation").glob("Blender*/blender.exe"), reverse=True)
    elif MAC:
        cands.append(Path("/Applications/Blender.app/Contents/MacOS/Blender"))
    return next((str(c) for c in cands if Path(c).exists()), None)


def main():
    strict = "--strict" in sys.argv

    v = run("node", "--version")
    m = re.match(r"v(\d+)", v)
    check("core", "Node.js 18+", bool(m and int(m.group(1)) >= 18), v or "not found",
          "install Node LTS: https://nodejs.org (Windows: winget install OpenJS.NodeJS.LTS · macOS: brew install node)")
    check("core", "npx", bool(shutil.which("npx")), shutil.which("npx") or "not found", "comes with Node.js")
    for tool in ("ffmpeg", "ffprobe"):
        out = run(tool, "-version")
        check("core", tool, out.startswith(f"{tool} version"), out.split("\n")[0][:60] or "not found",
              "Windows: winget install Gyan.FFmpeg · macOS: brew install ffmpeg · Linux: sudo apt install ffmpeg")
    py = sys.version_info
    check("core", "Python 3.10+", py >= (3, 10), platform.python_version(), "install Python 3.12 from python.org")
    for mod, pkg in (("numpy", "numpy"), ("PIL", "Pillow")):
        check("core", f"python: {pkg}", importlib.util.find_spec(mod) is not None,
              "installed" if importlib.util.find_spec(mod) else "missing", f"pip install -r {SKILL / 'requirements.txt'}")
    link = Path.home() / ".claude" / "skills" / "video-studio"
    linked = (link / "SKILL.md").exists()
    check("core", "skill visible to Claude Code", linked, str(link) if linked else "not linked",
          "run install/install.ps1 (Windows) or install/install.sh (macOS/Linux) from the repo")

    # voice tools often live in a side-by-side Python 3.12 (torch has no newer wheels yet)
    alt = (["py", "-3.12"] if WIN else ["python3.12"]) if py >= (3, 13) else None
    alt_ok = {}
    if alt:
        out = run(*alt, "-c", "import importlib.util as u;print(*[m for m in ('faster_whisper','torch','torchaudio') if u.find_spec(m)])")
        alt_ok = set(out.split()) if "Error" not in out and "not found" not in out.lower() else set()
    for mod, pkg in (("faster_whisper", "faster-whisper"), ("torch", "torch"), ("torchaudio", "torchaudio")):
        here = importlib.util.find_spec(mod) is not None
        there = mod in alt_ok
        check("voice", f"python: {pkg}", here or there,
              "installed" if here else f"installed in Python 3.12 (run with: {' '.join(alt)})" if there else "missing",
              f"Python 3.10-3.12, then: pip install -r {SKILL / 'requirements-voice.txt'}", core=False)
    if py >= (3, 13) and len(alt_ok) < 3:
        check("voice", "Python <= 3.12 for torch", False, platform.python_version(),
              "install Python 3.12 side by side and use it for transcribe.py / align.py (py -3.12 on Windows)", core=False)

    b = find_blender()
    bv = run(b, "--version").split("\n")[0] if b else ""
    m = re.search(r"Blender (\d+)\.(\d+)", bv)
    check("blender", "Blender 4.2+", bool(m and (int(m.group(1)), int(m.group(2))) >= (4, 2)), bv or "not found",
          "see INSTALL.md → Blender (Windows: winget install BlenderFoundation.Blender · macOS: brew install --cask blender)",
          core=False)
    smi = run("nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader")
    check("gpu", "NVIDIA GPU", bool(smi) and "not" not in smi.lower(), smi or "none (CPU works, slower)",
          "optional: speeds up Blender (OptiX) and Whisper", core=False)

    print(f"Video Studio doctor · {platform.system()} {platform.release()} · skill at {SKILL}\n")
    missing_core = 0
    for part, name, ok, have, fix, core in rows:
        mark = "✓" if ok else ("✗" if core else "–")
        print(f" {mark} [{part:7}] {name:30} {have}")
        if not ok:
            print(f"     {'fix' if core else 'optional'}: {fix}")
            missing_core += core
    print("\nCore ready: render videos." if not missing_core else f"\n{missing_core} core item(s) missing: fix those first.")
    sys.exit(1 if strict and missing_core else 0)


if __name__ == "__main__":
    main()
