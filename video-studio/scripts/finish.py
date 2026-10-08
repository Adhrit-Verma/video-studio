"""Finish a render for posting: final loudness, a poster, and the poster baked in as frame 0.

    python finish.py out/film.mp4 --beat 12.5 [--props out/props.json] [--config video.json]
    python finish.py out/film.mp4 --sec 6.8
      -> out/film.jpg (poster) and out/film.mp4 rewritten in place

--beat/--sec: the strongest SETTLED moment (text fully in, not mid-transition): the
reveal, the hook line, or the end card. Look at the contact sheet first; if the pulled
frame lands mid-motion, move it a few tenths and run again (it's idempotent).

1. Loudness: effects are mixed by Remotion on top of the -14 LUFS master, so the final
   mix can drift. If it's off by more than 0.5 LU or peaks above -1 dBTP, the audio is
   re-normalized (two-pass loudnorm); otherwise it's copied untouched.
2. Poster: that frame at full resolution -> <video>.jpg. Upload it as the custom
   thumbnail where platforms allow (Instagram, TikTok, YouTube, Facebook, LinkedIn), and
   use it as <video poster> on a site.
3. Frame 0 = poster: Slack, X and Discord make their own thumbnails from frame 0 and
   ignore cover-art metadata, so frame 0's pixels are replaced by the poster. Same frame
   count, same duration, audio timing untouched; on playback it shows for 1/30 s.
Needs ffmpeg/ffprobe on PATH.
"""
import sys
import argparse
import json
import re
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "loudnorm=I=-14:TP=-1:LRA=9:print_format=json",
                          "-vn", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return json.loads(re.findall(r"\{[^{}]*\}", err)[-1])


def frames(path):
    out = run("ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
              "stream=nb_read_packets", "-of", "csv=p=0", str(path)).stdout
    return int(out.strip().strip(","))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--beat", type=float)
    ap.add_argument("--sec", type=float)
    ap.add_argument("--props", default="out/props.json")
    ap.add_argument("--config", default="video.json")
    a = ap.parse_args()
    if (a.beat is None) == (a.sec is None):
        ap.error("give the poster moment as --beat or --sec")
    video = Path(a.video)
    sec = a.sec
    if a.beat is not None:
        props = Path(a.props)
        bpm = json.loads(props.read_text())["bpm"] if props.exists() else json.loads(Path(a.config).read_text())["bpm"]
        sec = a.beat * 60 / bpm

    poster = video.with_suffix(".jpg")
    run("ffmpeg", "-v", "error", "-y", "-ss", f"{sec:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(poster))

    has_audio = bool(run("ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                         "-of", "csv=p=0", str(video)).stdout.strip())
    m = loudness(video) if has_audio else None                  # a silent cut has nothing to normalize
    fix = bool(m) and (abs(float(m["input_i"]) + 14) > 0.5 or float(m["input_tp"]) > -1.0)
    if fix:
        af = (f"loudnorm=I=-14:TP=-1.0:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        audio = ["-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "256k"]
    else:
        audio = ["-c:a", "copy"]

    n0 = frames(video)
    tmp = video.with_name(video.stem + ".finishing.mp4")
    run("ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(poster),
        "-filter_complex", "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",
        "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
        *audio, "-movflags", "+faststart", str(tmp))
    n1 = frames(tmp)
    if n1 != n0:
        tmp.unlink()
        raise SystemExit(f"frame count changed ({n0} -> {n1}); left {video} untouched")
    tmp.replace(video)

    print(f"poster: {poster} (t={sec:.2f}s)")
    if not has_audio:
        print("loudness: no audio stream (silent cut)")
    else:
        after = loudness(video)
        print(f"loudness: {m['input_i']} LUFS / {m['input_tp']} dBTP"
              + (f" -> {after['input_i']} LUFS / {after['input_tp']} dBTP (re-normalized)" if fix else " (in range, audio copied)"))
    print(f"frame 0 = poster · {n1} frames, unchanged -> {video}")


if __name__ == "__main__":
    main()
