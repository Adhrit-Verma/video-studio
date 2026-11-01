"""Master a spoken voice track for a reel: de-hum, tone, de-ess, speech leveler, two-pass loudness + true-peak limit.

python master_voice.py <in.wav> <out.wav> [--target -14]     master one file, print before/after metrics
python master_voice.py --selfcheck                           synthetic test of the leveler + loudness

Techniques after projectalphatech/voice-cleaner (MIT): mains-hum notch only when a hum line is found, denoise
only when speech-to-noise is low (a denoiser can only blur clean speech), a leveler that rides each phrase toward
the median speech level while pauses stay put, and two-pass linear loudnorm instead of a one-pass guess.
"""
import json, re, subprocess, sys
import numpy as np

SR = 48000
TONE = ",".join([
    "equalizer=f=250:t=q:w=1.2:g=-3",           # de-mud
    "equalizer=f=3200:t=q:w=1.0:g=3",           # presence / clarity
    "highshelf=f=10000:g=2",                    # air
    "deesser=i=0.4",
    "acompressor=threshold=-22dB:ratio=2:attack=10:release=150:makeup=2",   # gentle: the leveler does the riding
])


def ff(args, data=None, log="error"):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", log, "-y", *args], input=data, capture_output=True,
                       stdin=None if data is not None else subprocess.DEVNULL)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors="replace")[-400:])
    return p


def decode(path):
    return np.frombuffer(ff(["-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "pipe:1"]).stdout, np.float32).copy()


RAW = ["-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "pipe:0"]


def filt(x, chain):
    return np.frombuffer(ff([*RAW, "-af", chain, "-f", "f32le", "pipe:1"], x.astype(np.float32).tobytes()).stdout, np.float32).copy()


def hum(x):
    """50 or 60 if a mains line (or its 2nd/3rd harmonic) stands 20 dB over its neighbourhood, else None."""
    m = x[: SR * 120]
    if len(m) < SR:
        return None
    spec, hz = np.abs(np.fft.rfft(m * np.hanning(len(m)))), np.fft.rfftfreq(len(m), 1 / SR)
    score = lambda f: max(spec[abs(hz - k * f) < 1].max() / (np.median(spec[abs(hz - k * f) < 15]) + 1e-12) for k in (1, 2, 3))
    best = max((50, 60), key=score)
    return best if score(best) > 10 else None


def frames(x):
    """400 ms RMS dB every 50 ms + speech mask (10 dB over the floor and within 30 dB of the loudest speech)."""
    hop = SR // 20
    n = len(x) // hop
    db = 10 * np.log10(np.convolve((x[: n * hop].reshape(n, hop) ** 2).mean(1), np.ones(8) / 8, "same") + 1e-12)
    floor = np.percentile(db, 10)
    return db, db > max(floor + 10, np.percentile(db, 95) - 30)


def snr(x):
    db, sp = frames(x)
    return 0.0 if sp.sum() < 10 or sp.all() else float(np.median(db[sp]) - np.median(db[~sp]))


def smooth(v, a):
    """Zero-phase one-pole smoothing (forward then backward), so gain can anticipate word onsets."""
    v = v.copy()
    for order in (range(len(v)), range(len(v) - 1, -1, -1)):
        cur = v[order[0]]
        for i in order:
            cur += a * (v[i] - cur)
            v[i] = cur
    return v


def level(x, max_gain=9.0, amount=0.7):
    """Ride speech `amount` of the way toward its median level (±max_gain dB): even, but still expressive.
    Pauses keep the gain of the speech beside them."""
    hop = SR // 20
    db, sp = frames(x)
    if sp.sum() < 10:
        return x
    idx = np.arange(len(db))
    want = smooth(np.interp(idx, idx[sp], np.clip(amount * (np.median(db[sp]) - db[sp]), -max_gain, max_gain)), 0.15)
    return (x * 10 ** (np.interp(np.arange(len(x)), idx * hop + hop / 2, want) / 20)).astype(np.float32)


def lufs(x):
    err = ff([*RAW, "-af", "ebur128", "-f", "null", "-"], x.tobytes(), "info").stderr.decode()
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def loudnorm(x, target, tp=-1.5):
    """Exact gain to target, then a fast peak limiter at the true-peak ceiling; repeated, since limiting costs a little."""
    for _ in range(4):
        x = filt(x, f"volume={target - lufs(x):.2f}dB,alimiter=limit={10 ** (tp / 20):.3f}:attack=1:release=50:level=false")
    return x


def master(x, target=-14):
    h = hum(x)
    chain = ["highpass=f=85"] + ([f"bandreject=f={h * k}:t=h:w=2" for k in range(1, 7)] if h else [])
    x = filt(x, ",".join(chain))
    s = snr(x)
    if s <= 40:                                  # noisy enough to need it; clean phone takes skip this
        x = filt(x, "afftdn=nr=10:nf=-50:tn=1")
    x = loudnorm(filt(level(x), TONE), target)
    return x, {"hum_hz": h, "speech_to_noise_db": round(s, 1), "denoised": s <= 40}


def stats(x):
    err = ff([*RAW, "-af", "ebur128=peak=true", "-f", "null", "-"], x.tobytes(), "info").stderr.decode()
    db, sp = frames(x)
    p = db[sp]
    return {"LUFS": float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), "true peak dBTP": float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1]),
            "loudness range LU": float(re.findall(r"LRA:\s+(-?[\d.]+) LU", err)[-1]), "speech spread p10-p90 dB": float(np.percentile(p, 90) - np.percentile(p, 10))}


def write(x, path):
    ff([*RAW, "-c:a", "pcm_s24le", path], x.astype(np.float32).tobytes())


def selfcheck():
    rng = np.random.default_rng(0)
    def talk(db, s):                              # voice-band noise with a 4 Hz syllable envelope
        n = int(SR * s); v = filt(rng.standard_normal(n).astype(np.float32), "bandpass=f=1000:t=h:w=1500")
        v *= 0.5 * (1 + np.sin(2 * np.pi * 4 * np.arange(n) / SR)); return v / np.sqrt((v ** 2).mean()) * 10 ** (db / 20)
    gap = np.zeros(SR, np.float32)
    x = np.concatenate([gap, talk(-20, 6), gap, talk(-32, 6), gap]).astype(np.float32)
    x += (0.01 * np.sin(2 * np.pi * 50 * np.arange(len(x)) / SR)).astype(np.float32)
    y, info = master(x)
    rms = lambda a, b: 10 * np.log10((y[int(a * SR):int(b * SR)] ** 2).mean())
    assert info["hum_hz"] == 50, info
    assert abs(stats(y)["LUFS"] + 14) < 1, stats(y)
    assert stats(y)["true peak dBTP"] <= -0.5, stats(y)
    assert abs(rms(1.5, 6.5) - rms(8.5, 13.5)) < 6, "leveler must close most of the 12 dB gap"
    print("selfcheck ok", info)


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        selfcheck(); sys.exit()
    src, dst = sys.argv[1], sys.argv[2]
    target = float(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else -14
    x = decode(src)
    y, info = master(x, target)
    write(y, dst)
    a, b = stats(x), stats(y)
    print(info)
    for k in a:
        print(f"{k:28}{a[k]:9.1f} -> {b[k]:6.1f}")
