<#
Install the Video Studio skill on Windows, the same way it runs on the original machine.

  .\install\install.ps1                  core: Node/ffmpeg/Python checks, Python packages, link the skill
  .\install\install.ps1 -Deps            also install missing Node LTS, ffmpeg, Python 3.12 with winget
  .\install\install.ps1 -Voice           also the voice/lyric tools (faster-whisper, torch) in Python 3.12
  .\install\install.ps1 -Blender         also Blender (photoreal product shots; UAC prompt)
  .\install\install.ps1 -All             everything above

The skill is LINKED (a junction), not copied: `git pull` in this repo updates it.
Finishes by running scripts\doctor.py, which lists anything still missing.
#>
param([switch]$Deps, [switch]$Voice, [switch]$Blender, [switch]$All)
$ErrorActionPreference = "Continue"   # native tools write notices to stderr; PS 5.1 would abort on them
if ($All) { $Deps = $true; $Voice = $true; $Blender = $true }

$Repo  = Split-Path -Parent $PSScriptRoot
$Skill = Join-Path $Repo "video-studio"
if (-not (Test-Path (Join-Path $Skill "SKILL.md"))) { throw "Run this from the cloned repo (video-studio\SKILL.md not found)." }

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Winget {
  $w = Get-Command winget -ErrorAction SilentlyContinue
  if ($w) { return $w.Source }
  $alt = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\winget.exe"
  if (Test-Path $alt) { return $alt }
  return $null
}
function WingetInstall($id) {
  $w = Winget
  if (-not $w) { Write-Warning "winget not found: install $id by hand (see INSTALL.md)"; return }
  Write-Host "  installing $id ..." -ForegroundColor Cyan
  & $w install --id $id -e --accept-source-agreements --accept-package-agreements --silent
}
function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Host "`n== Video Studio: install ==" -ForegroundColor Green

# 1. system tools
if ($Deps) {
  if (-not (Have node))   { WingetInstall "OpenJS.NodeJS.LTS" }
  if (-not (Have ffmpeg)) { WingetInstall "Gyan.FFmpeg" }
  if (-not (Have python) -and -not (Have py)) { WingetInstall "Python.Python.3.12" }
  Refresh-Path
}
foreach ($t in "node", "ffmpeg") { if (-not (Have $t)) { Write-Warning "$t is missing: re-run with -Deps, or see INSTALL.md" } }

# 2. Python packages (core) into the default Python
$Py = if (Have python) { "python" } elseif (Have py) { "py" } else { $null }
if ($Py) {
  Write-Host "  python packages (core) ..." -ForegroundColor Cyan
  & $Py -m pip install --user -q --disable-pip-version-check -r (Join-Path $Skill "requirements.txt")
} else { Write-Warning "Python not found: re-run with -Deps" }

# 3. voice/lyric tools need Python <= 3.12 (torch wheels)
if ($Voice) {
  $has312 = $false
  if (Have py) { & py -3.12 -c "import sys" 2>$null; $has312 = ($LASTEXITCODE -eq 0) }
  if (-not $has312) { WingetInstall "Python.Python.3.12"; Refresh-Path; & py -3.12 -c "import sys" 2>$null; $has312 = ($LASTEXITCODE -eq 0) }
  if ($has312) {
    Write-Host "  voice tools into Python 3.12 (large download) ..." -ForegroundColor Cyan
    & py -3.12 -m pip install --user -q --disable-pip-version-check -r (Join-Path $Skill "requirements-voice.txt")
    Write-Host "  run them with: py -3.12 video-studio\scripts\transcribe.py ..." -ForegroundColor DarkGray
  } else { Write-Warning "Python 3.12 not available: voice tools skipped (see INSTALL.md)" }
}

# 4. Blender
if ($Blender) {
  $found = Get-ChildItem "$env:ProgramFiles\Blender Foundation" -Filter blender.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $found -and -not (Have blender)) { WingetInstall "BlenderFoundation.Blender" } else { Write-Host "  Blender already installed" }
}

# 5. link the skill where Claude Code looks for it
$SkillsDir = Join-Path $env:USERPROFILE ".claude\skills"
$Link = Join-Path $SkillsDir "video-studio"
New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
if (Test-Path $Link) {
  $item = Get-Item $Link -Force
  if ($item.LinkType -and ($item.Target -contains $Skill -or "$($item.Target)" -eq $Skill)) {
    Write-Host "  skill already linked"
  } else {
    $bak = "$Link.bak-$(Get-Date -Format yyyyMMddHHmmss)"
    Write-Host "  moving the existing $Link to $bak"
    Move-Item $Link $bak
    New-Item -ItemType Junction -Path $Link -Target $Skill | Out-Null
  }
} else {
  New-Item -ItemType Junction -Path $Link -Target $Skill | Out-Null
  Write-Host "  linked $Link -> $Skill"
}

# 6. report
Write-Host ""
if ($Py) { & $Py (Join-Path $Skill "scripts\doctor.py") }
Write-Host "`nDone. Start a new Claude Code session and ask: 'make a launch video for this project'." -ForegroundColor Green
