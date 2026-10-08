"""Mix voiceover lines over a music track: the song plays as it is (no cuts), each line
lands at its time, the music ducks under every line, a warm reverb tail follows the
song's last note, and the mix is mastered to -14 LUFS / -1 dBTP.

    python mix_voice.py --music public/song.mp3 --lines public/vo/lines.json
                        [--out public/mix.wav] [--duck 10] [--tail 2.5] [--vo-gain 0]

lines.json: [{"id": "01", "start": 1.5, ...}, ...]; the WAVs sit next to it as <id>.wav.
Ducking: -duck dB under each line, a 150 ms fall before it and a 450 ms recovery after
(smooth cosine ramps; no pumping). Voices are high-passed at 90 Hz and evened out to the
same loudness before they go in. Prints the total length: set video.json totalBeats to it
(bpm 60 = seconds) and pass {"music": "<out>", "bpm": 60, "offset": 0} as props.
Needs numpy and ffmpeg.
"""
import sys
import argparse
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 44100


def load(path, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", str(ch), "-ar", str(SR), "-af", "highpass=f=90" if ch == 1 else "anull",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, ch).astype(np.float64)


def ramp(n):
    return 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, max(1, n)))


def reverb_tail(x, seconds):
    rng = np.random.default_rng(5)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros((len(x) + n, 2))
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t / (seconds / 4.5))
        ir = np.convolve(ir, np.ones(24) / 24, "same")              # warm: no hiss
        ir /= np.sqrt(np.sum(ir ** 2))
        size = 1 << int(np.ceil(np.log2(len(x) + n)))
        out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], size) * np.fft.rfft(ir, size), size)[: len(x) + n]
    return out


def loudnorm(src, dst):
    first = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(re.findall(r"\{[^{}]*\}", first)[-1])
    af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ar", str(SR), str(dst)], check=True)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", required=True)
    ap.add_argument("--lines", required=True)
    ap.add_argument("--out", default="public/mix.wav")
    ap.add_argument("--duck", type=float, default=10.0)
    ap.add_argument("--tail", type=float, default=2.5)
    ap.add_argument("--vo-gain", type=float, default=0.0, help="dB, voices relative to the default balance")
    ap.add_argument("--nudge", type=float, default=0.026,
                    help="s; starts the mix this much early to cancel the AAC encoder delay (as master_audio.py does)")
    a = ap.parse_args()
    song = load(a.music)
    lines = json.loads(Path(a.lines).read_text(encoding="utf-8"))
    # the song's last 1.2 s feed a reverb that rings past its end
    tail = reverb_tail(song[-int(1.2 * SR):], a.tail)[int(1.2 * SR):] * 0.35
    fade = np.linspace(1, 0, len(tail)) ** 1.5
    music = np.vstack([song, tail * fade[:, None]])
    n = len(music)

    gain = np.ones(n)
    fall, rise = int(0.15 * SR), int(0.45 * SR)
    low = 10 ** (-a.duck / 20)
    voice = np.zeros((n, 2))
    for ln in lines:
        v = load(Path(a.lines).parent / f"{ln['id']}.wav", ch=1)[:, 0]
        v /= max(1e-9, np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)))   # even loudness across lines
        v *= 0.11 * 10 ** (a.vo_gain / 20)
        s = int(ln["start"] * SR)
        e = min(n, s + len(v))
        voice[s:e] += v[: e - s, None]
        d0, d1 = max(0, s - fall), min(n, e + rise)
        env = np.full(d1 - d0, low)
        env[: s - d0] = 1 - (1 - low) * ramp(s - d0)
        env[e - d0:] = low + (1 - low) * ramp(d1 - e)
        gain[d0:d1] = np.minimum(gain[d0:d1], env)
    mix = music * gain[:, None] + voice
    k = int(a.nudge * SR)                                          # encoder delay: start early, keep the length
    mix = np.vstack([mix[k:], np.zeros((k, 2))])
    raw = Path(a.out).with_name(Path(a.out).stem + "_premaster.wav")
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix / max(1e-9, np.abs(mix).max()) * 0.92, -1, 1) * 32767).astype("<i2").tobytes())
    m = loudnorm(raw, a.out)
    print(f"{a.out}: {n / SR:.2f}s ({len(lines)} lines, music -{a.duck:g} dB under voice) · was {m['input_i']} LUFS -> -14 LUFS / -1 dBTP")
    print(f"-> totalBeats {n / SR:.2f} at bpm 60; props {{\"music\": \"{Path(a.out).name}\", \"bpm\": 60, \"offset\": 0}}")


if __name__ == "__main__":
    main()
