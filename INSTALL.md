# Installing Video Studio on a new machine

> **For Claude Code:** if a user asks you to "install the video-studio skill" (or points you at
> this repo), follow this file top to bottom. Ask before steps marked **(asks first)**: they
> install system software. Finish with the doctor and report its output.

## 1. Clone the repo

Pick a permanent folder; the skill is **linked** from it, so don't clone into a temp dir.

```bash
git clone https://github.com/Adhrit-Verma/video-studio.git
cd video-studio
```

## 2. Run the installer

| | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Core | `powershell -ExecutionPolicy Bypass -File install\install.ps1` | `bash install/install.sh` |
| + system tools **(asks first)** | `... install.ps1 -Deps` | `bash install/install.sh --deps` |
| + voice / lyric tools **(asks first)** | `... install.ps1 -Voice` | `bash install/install.sh --voice` |
| + Blender **(asks first)** | `... install.ps1 -Blender` | `bash install/install.sh --blender` |
| Everything | `... install.ps1 -All` | `bash install/install.sh --all` |

What it does:
1. Checks Node, ffmpeg and Python (with `-Deps`/`--deps` it installs missing ones through
   winget, Homebrew or apt).
2. Installs the Python packages (`video-studio/requirements.txt`: numpy, Pillow).
3. **Links** `video-studio/` to `~/.claude/skills/video-studio` (a junction on Windows, a
   symlink elsewhere), so `git pull` updates the skill. An existing folder there is moved to
   `video-studio.bak-<date>`, not deleted.
4. Runs `video-studio/scripts/doctor.py`, which prints a ✓/✗ table with the fix for each gap.

Then **start a new Claude Code session**: skills load at session start.

## 3. What each part needs

| Part | Needed for | Requirement |
|---|---|---|
| **Core** | every video | Node.js 18+ (npm, npx) · ffmpeg + ffprobe on `PATH` · Python 3.10+ with numpy, Pillow |
| **Voice / lyrics** | voice notes, captions, lyric edits (`transcribe.py`, `align.py`, `retime_captions.py`) | Python **3.10–3.12** (torch has no wheels for 3.13+) with `requirements-voice.txt`: faster-whisper, torch, torchaudio (~2–3 GB with models) |
| **Blender** | photoreal product/device shots (`blender_product_shot.py`) | Blender **4.2+** (tested with 5.2 LTS) |
| GPU (optional) | faster Blender (OptiX) and Whisper | NVIDIA with recent drivers; everything also runs on CPU |

Each video project installs its own Remotion packages the first time (`npm install` in the
project, about a minute). Nothing global is needed for Remotion.

## 4. Manual install, if the installer can't

**Node.js 18+:** https://nodejs.org (LTS) · Windows `winget install OpenJS.NodeJS.LTS` · macOS `brew install node` · Ubuntu `sudo apt install nodejs npm` (or NodeSource for a newer version).

**ffmpeg:** Windows `winget install Gyan.FFmpeg` (then open a new terminal so `PATH` updates) · macOS `brew install ffmpeg` · Ubuntu `sudo apt install ffmpeg`.

**Python packages:**
```bash
python -m pip install --user -r video-studio/requirements.txt
```

**Voice / lyric tools** (side by side with a newer Python is fine):
```bash
# Windows: winget install Python.Python.3.12, then
py -3.12 -m pip install --user -r video-studio/requirements-voice.txt
# macOS / Linux
python3.12 -m pip install --user -r video-studio/requirements-voice.txt
```
For NVIDIA GPU speed, install torch + torchaudio from https://pytorch.org (pick your CUDA)
before the line above. Run the tools with that Python: `py -3.12 video-studio/scripts/transcribe.py …`.
The first run downloads Whisper large-v3 and the MMS aligner (~3 GB, cached).

**Link the skill by hand:**
```powershell
# Windows
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\video-studio" -Target "$PWD\video-studio"
```
```bash
# macOS / Linux
mkdir -p ~/.claude/skills && ln -s "$PWD/video-studio" ~/.claude/skills/video-studio
```

## 5. Blender

Only needed for photoreal device or product hero shots; UI, type and 3D-UI scenes are built
in Remotion. **(asks first)**: it's a ~400 MB install and raises an admin prompt on Windows.

| OS | Install | Where it lands |
|---|---|---|
| Windows | `winget install BlenderFoundation.Blender` (if `winget` isn't on `PATH`, it's often at `%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe`) or the installer from https://www.blender.org/download/ | `C:\Program Files\Blender Foundation\Blender <ver>\blender.exe` |
| macOS | `brew install --cask blender` | `/Applications/Blender.app/Contents/MacOS/Blender` |
| Linux | `sudo snap install blender --classic`, or the official tarball | `blender` on `PATH` |

Check it, then try a headless test frame:

```bash
blender --version          # want 4.2 or newer
blender -b -P video-studio/scripts/blender_product_shot.py -- --screen docs/poster.jpg --out out/test --frames 1
```
On Windows use the full path to `blender.exe` if it isn't on `PATH`. The doctor finds the
standard install locations either way. Scripts run headless (`-b`); no Blender add-ons or MCP
are needed. GPU rendering uses OptiX on NVIDIA cards and falls back to CPU automatically.

## 6. Verify

```bash
python video-studio/scripts/doctor.py
```
`Core ready: render videos.` means you can make films. Optional parts show `–` with how to add
them. For a full end-to-end check, ask Claude Code in any project: *"make a 10-second test
video for this project"*.

## Updating

```bash
git pull
```
The link means the skill updates in place; start a new Claude Code session to load it.

## Machine notes
- **Laptops:** keep Remotion's default render concurrency and don't use `--gl=angle`.
  Higher settings have crashed a 16 GB laptop. Iterate with stills and `--scale=0.5` drafts.
- **Windows:** the scripts force UTF-8 output, so non-ASCII titles (Hindi, curly quotes)
  are safe in any console.
- **claude.ai / Claude desktop (no terminal):** upload `dist/video-studio.skill` under
  Settings → Capabilities → Skills. Rendering still needs a machine with the core tools.
