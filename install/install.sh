#!/usr/bin/env bash
# Install the Video Studio skill on macOS or Linux, the same way it runs on the original machine.
#
#   ./install/install.sh             core: checks, Python packages, link the skill
#   ./install/install.sh --deps      also install missing Node, ffmpeg, Python (Homebrew / apt)
#   ./install/install.sh --voice     also the voice/lyric tools (faster-whisper, torch; Python <= 3.12)
#   ./install/install.sh --blender   also Blender (photoreal product shots)
#   ./install/install.sh --all       everything above
#
# The skill is SYMLINKED, not copied: `git pull` in this repo updates it.
# Finishes by running scripts/doctor.py, which lists anything still missing.
set -euo pipefail

DEPS=0 VOICE=0 BLENDER=0
for a in "$@"; do
  case "$a" in
    --deps) DEPS=1 ;; --voice) VOICE=1 ;; --blender) BLENDER=1 ;;
    --all) DEPS=1; VOICE=1; BLENDER=1 ;;
    *) echo "unknown option: $a"; exit 2 ;;
  esac
done

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SKILL="$REPO/video-studio"
[ -f "$SKILL/SKILL.md" ] || { echo "Run this from the cloned repo (video-studio/SKILL.md not found)."; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }
OS="$(uname -s)"

pkg() {   # install a package with the system's manager
  if [ "$OS" = "Darwin" ]; then
    have brew || { echo "Homebrew missing: https://brew.sh"; return 1; }
    brew install "$@"
  elif have apt-get; then sudo apt-get update -qq && sudo apt-get install -y "$@"
  elif have dnf; then sudo dnf install -y "$@"
  else echo "install $* by hand (see INSTALL.md)"; return 1
  fi
}

echo; echo "== Video Studio: install =="

if [ $DEPS = 1 ]; then
  have node   || { [ "$OS" = "Darwin" ] && pkg node || pkg nodejs npm; }
  have ffmpeg || pkg ffmpeg
  have python3 || { [ "$OS" = "Darwin" ] && pkg python@3.12 || pkg python3 python3-pip; }
fi
for t in node ffmpeg python3; do have $t || echo "WARNING: $t missing: re-run with --deps, or see INSTALL.md"; done

echo "  python packages (core) ..."
python3 -m pip install --user -q --disable-pip-version-check -r "$SKILL/requirements.txt" 2>/dev/null \
  || python3 -m pip install --user -q --disable-pip-version-check --break-system-packages -r "$SKILL/requirements.txt"

if [ $VOICE = 1 ]; then
  PY312=""
  for c in python3.12 python3.11 python3.10; do have $c && { PY312=$c; break; }; done
  if [ -z "$PY312" ]; then
    [ "$OS" = "Darwin" ] && pkg python@3.12 && PY312=python3.12
  fi
  if [ -n "$PY312" ]; then
    echo "  voice tools into $PY312 (large download) ..."
    $PY312 -m pip install --user -q --disable-pip-version-check -r "$SKILL/requirements-voice.txt" 2>/dev/null \
      || $PY312 -m pip install --user -q --disable-pip-version-check --break-system-packages -r "$SKILL/requirements-voice.txt"
    echo "  run them with: $PY312 video-studio/scripts/transcribe.py ..."
  else
    echo "WARNING: no Python 3.10-3.12 found: voice tools skipped (see INSTALL.md)"
  fi
fi

if [ $BLENDER = 1 ]; then
  if have blender || [ -x /Applications/Blender.app/Contents/MacOS/Blender ]; then echo "  Blender already installed"
  elif [ "$OS" = "Darwin" ]; then brew install --cask blender
  elif have snap; then sudo snap install blender --classic
  else echo "Install Blender 4.2+ from https://www.blender.org/download/ and put 'blender' on PATH"
  fi
fi

mkdir -p "$HOME/.claude/skills"
LINK="$HOME/.claude/skills/video-studio"
if [ -L "$LINK" ] && [ "$(readlink "$LINK")" = "$SKILL" ]; then
  echo "  skill already linked"
else
  if [ -e "$LINK" ] || [ -L "$LINK" ]; then
    BAK="$LINK.bak-$(date +%Y%m%d%H%M%S)"; echo "  moving the existing $LINK to $BAK"; mv "$LINK" "$BAK"
  fi
  ln -s "$SKILL" "$LINK"; echo "  linked $LINK -> $SKILL"
fi

echo
python3 "$SKILL/scripts/doctor.py" || true
echo; echo "Done. Start a new Claude Code session and ask: 'make a launch video for this project'."
