"""An original beat (minimal or phonk style), synthesised from scratch (no samples, no
copyrighted audio), arranged on the video's beat grid from video.json.

    python gen_beat.py [--config video.json] [--style minimal|phonk]   (genre comes from the brief)

  -> public/beat.wav
  -> out/sync.json   {music, bpm, offset: 0, kicks, kickWeights}  (exact, no analysis needed)

Arrangement (beats, from video.json):
  [0, dropBeat-8)  intro: the bell riff through a wall (filtered), no drums
  [dropBeat-8, dropBeat)  build: hats, riser, snare roll into the drop
  dropBeat  DROP: kick, 808, clap, hats, crash
  breaks  [[a, b], ...]: drums out (the bell carries on), crash back in on b
  endBeat  final hit: kick + long 808 + crash, then a reverb tail to totalBeats
Needs numpy. Safe to post anywhere: every sound is generated here.
"""
import sys
import argparse
import json
import wave
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SR = 44100
rng = np.random.default_rng(7)


def t(n):
    return np.arange(n) / SR


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, "same")


def hp(x, k):
    return x - lp(x, k)


def cowbell(freq):
    n = int(0.32 * SR)
    tt = t(n)
    sq = lambda f: np.sign(np.sin(2 * np.pi * f * tt))  # noqa: E731
    s = lp(hp(0.6 * sq(freq) + 0.4 * sq(freq * 1.48), 10), 3)
    return np.tanh(1.6 * s * (0.8 * np.exp(-tt / 0.085) + 0.4 * np.exp(-tt / 0.012))) * 0.42


def pluck(freq):                                         # the "minimal" style's lead: a soft sine pluck
    n = int(0.5 * SR)
    tt = t(n)
    return (np.sin(2 * np.pi * freq * tt) + 0.3 * np.sin(4 * np.pi * freq * tt)) * np.exp(-tt / 0.18) * 0.3


def kick():
    n = int(0.42 * SR)
    tt = t(n)
    f = 44 + 120 * np.exp(-tt / 0.028)
    return np.tanh(2.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.17)) * 0.95


def bass(freq, dur):
    n = int(dur * SR)
    tt = t(n)
    f = freq * (1 + 0.9 * np.exp(-tt / 0.02))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt / 0.004) * np.exp(-tt / (dur * 0.6))
    return np.tanh(3.2 * s) * 0.5


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    return hp(hp(rng.standard_normal(n), 3), 3) * np.exp(-t(n) / (0.07 if open_ else 0.016)) * 0.16


def clap():
    n = int(0.32 * SR)
    s = hp(lp(rng.standard_normal(n), 3), 24)
    e = np.zeros(n)
    for d, dec in ((0, 0.01), (0.012, 0.01), (0.024, 0.13)):
        i = int(d * SR)
        e[i:] += np.exp(-t(n - i) / dec)
    return s * e * 0.33


def crash():
    n = int(2.2 * SR)
    return hp(rng.standard_normal(n), 2) * np.exp(-t(n) / 0.75) * 0.11


def riser(seconds):
    n = int(seconds * SR)
    tt = t(n)
    ramp = (tt / tt[-1]) ** 2
    sweep = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (3.5 * tt / tt[-1])) / SR)
    return (hp(rng.standard_normal(n), 4) * 0.12 + sweep * 0.05) * ramp


def reverb(x, seconds=1.5, decay=0.5):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-t(n) / decay)
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="video.json")
    ap.add_argument("--style", default="minimal", choices=["minimal", "phonk"])
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    bpm, total, drop = cfg["bpm"], cfg["totalBeats"], cfg["dropBeat"]
    end = cfg.get("endBeat", total - 6)
    breaks = [tuple(x) for x in cfg.get("breaks", [])]
    beat = 60 / bpm
    N = int((total * beat + 0.3) * SR)
    build = max(0, drop - 8)

    def place(bus, sig, b, gain=1.0):
        i = int(b * beat * SR)
        if 0 <= i < N:
            j = min(N, i + len(sig))
            bus[i:j] += sig[: j - i] * gain

    in_break = lambda b: any(x <= b < y for x, y in breaks)   # noqa: E731
    drums_on = lambda b: drop <= b < end and not in_break(b)  # noqa: E731
    lead, kik, snr, hats, sub, fx = (np.zeros(N) for _ in range(6))
    semi = lambda f, s: f * 2 ** (s / 12)                     # noqa: E731
    RIFF = [(0, 0), (3, 0), (6, 3), (8, 5), (11, 3), (14, 0),
            (16, 7), (19, 5), (22, 3), (24, 0), (26, -2), (28, 0), (30, 3)]    # (16th, semitone), 2 bars
    BASS = [(0, 0, 6), (6, 0, 3), (10, 3, 5), (16, 0, 6), (22, 5, 3), (26, -2, 5)]
    voice, root = (cowbell, 587.0) if a.style == "phonk" else (pluck, 440.0)

    kicks = []
    for bar2 in range(0, end, 8):
        for pos, s in RIFF:
            place(lead, voice(semi(root, s)), bar2 + pos / 4)
        for pos, s, ln in BASS:
            b = bar2 + pos / 4
            if drums_on(b):
                place(sub, bass(semi(46.25, s), ln * beat / 4 * 1.15), b)
    for b16 in range(0, end * 4):
        b = b16 / 4
        slot = b16 % 16
        if drums_on(b):
            if slot in (0, 10) or (int(b) // 4 % 2 == 1 and slot == 7):
                place(kik, kick(), b)
                kicks.append((b, 1.0 if slot == 0 else 0.8))
            if slot in (4, 12):
                place(snr, clap(), b)
            if b16 % 2 == 0:
                place(hats, hat(open_=(slot == 14 and int(b) // 4 % 2 == 0)), b, 0.9 if b16 % 4 else 1.1)
        elif build <= b < build + 4 and b16 % 2 == 0:
            place(hats, hat(), b, 0.7)
        elif build + 4 <= b < drop:
            place(hats, hat(), b, 0.5 + 0.5 * (b - build - 4) / 4)
            if b >= drop - 2:
                place(snr, clap(), b, 0.3 + 0.7 * (b - drop + 2) / 2)
    if drop - build >= 4:
        place(fx, riser((drop - build - 0.0) * beat * 0.5), build + (drop - build) / 2)
    have = {kb for kb, _ in kicks}
    for b in [drop] + [y for _, y in breaks] + [end]:
        place(fx, crash(), b)
        if b not in have:                                   # the pattern may already kick here
            place(kik, kick(), b)
            kicks.append((b, 1.0))
            have.add(b)
    place(sub, bass(46.25, 2.6), end, 1.1)
    place(lead, voice(root), end, 1.2)

    i_build = int(build * beat * SR)
    if i_build:
        lead[:i_build] = lp(lead[:i_build], 14) * 0.7            # the intro, through a wall

    duck = np.ones(N)                                            # sidechain under the kick
    for kb, _ in kicks:
        i = int(kb * beat * SR)
        n = min(N - i, int(0.22 * SR))
        if n > 0:
            duck[i:i + n] = np.minimum(duck[i:i + n], 1 - 0.55 * np.exp(-t(n) / 0.09))
    wet_l, wet_r = reverb(lead), reverb(lead)
    pan = 0.15 * np.sin(np.arange(N) / SR * 2 * np.pi * 0.9)
    left = (lead + 0.35 * wet_l + sub) * duck + kik + snr + hats * (1 - pan) + fx
    right = (lead + 0.35 * wet_r + sub) * duck + kik + snr + hats * (1 + pan) + fx
    mix = np.tanh(1.15 * np.stack([left, right], axis=1))
    mix /= np.abs(mix).max() / 0.89
    fade = int(0.6 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]

    out = Path("public") / "beat.wav"
    out.parent.mkdir(exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    kicks.sort()
    sync = {"music": out.name, "bpm": bpm, "offset": 0, "generated": True,
            "kicks": [round(b * beat, 3) for b, _ in kicks], "kickWeights": [w for _, w in kicks]}
    Path("out").mkdir(exist_ok=True)
    Path("out/sync.json").write_text(json.dumps(sync))
    Path("out/props.json").write_text(json.dumps(sync))
    print(f"{out} · {N / SR:.1f}s · {bpm} BPM · {len(kicks)} kicks -> out/sync.json, out/props.json")


if __name__ == "__main__":
    main()
