"""Procedural, royalty-free soundtrack for the Casa Alberto reels.

Usage: python3 soundtrack.py cues.json out.wav

cues.json: {"duration": 23, "style": "chill|trap|upbeat", "bpm": 96,
            "sfx": [{"t": 1.2, "type": "whoosh"}, ...]}
"""
import json
import sys
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(42)


def note(n):
    """MIDI note number -> Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def env_ad(n, attack, decay_tau):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay_tau)


def fft_filter(x, lo=0.0, hi=SR / 2):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = np.ones_like(f)
    if lo > 0:
        mask *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi < SR / 2:
        mask *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec * mask, len(x))


def add(buf, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[0] or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    sig = sig[: buf.shape[0] - i]
    buf[i:i + len(sig), 0] += sig * gain * (1 - max(pan, 0))
    buf[i:i + len(sig), 1] += sig * gain * (1 + min(pan, 0))


# ---------------------------------------------------------------- instruments
def kick(length=0.45, punch=1.0, sub=False):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 45 + 120 * np.exp(-t * 28) * punch
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / (0.9 if sub else 0.16))
    click = rng.standard_normal(n) * np.exp(-t * 300) * 0.3
    return np.tanh((body + click) * (1.8 if sub else 1.4))


def snare(length=0.3, tone=190):
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = fft_filter(rng.standard_normal(n), 1200, 9000) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * tone * t) * np.exp(-t * 30)
    return noise * 0.9 + body * 0.6


def clap(length=0.3):
    n = int(length * SR)
    t = np.arange(n) / SR
    e = np.zeros(n)
    for d in (0, 0.011, 0.022):
        e += np.where(t >= d, np.exp(-(t - d) * (60 if d < .02 else 14)), 0)
    return fft_filter(rng.standard_normal(n), 900, 7000) * e * 0.8


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    return fft_filter(rng.standard_normal(n), 7000) * np.exp(-t * (12 if open_ else 70))


def keys(freqs, length, bright=1.0, trem=0.0):
    """Electric-piano-ish chord."""
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        out += np.sin(2 * np.pi * f * t + 0.7 * bright * np.sin(2 * np.pi * f * t) * np.exp(-t * 4))
        out += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    out *= env_ad(n, 0.005, length * 0.7) / len(freqs)
    if trem:
        out *= 1 - trem * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))
    return out


def pad(freqs, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for d in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (d / 12)
            out += 2 * ((ff * t) % 1) - 1
    out = fft_filter(out, 80, 1800) / (len(freqs) * 3)
    a = np.clip(t / 0.25, 0, 1) * np.clip((length - t) / 0.3, 0, 1)
    return out * a


def bass(f, length, sub=False):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t)
    if not sub:
        s += 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sign(np.sin(2 * np.pi * f * t))
    e = np.clip(t / 0.005, 0, 1) * np.clip((length - t) / 0.02, 0, 1)
    if sub:
        e *= np.exp(-t * 1.2)
    return np.tanh(s * e * 1.3) * 0.8


def pluck(f, length=0.35):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = (2 * ((f * t) % 1) - 1) + 0.5 * np.sin(2 * np.pi * 2 * f * t)
    return fft_filter(s * np.exp(-t * 9), 0, 3500) * 0.5


# ---------------------------------------------------------------- sound effects
def whoosh(length=0.6, rising=True):
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    bands = [fft_filter(noise, c * 0.6, c * 1.6) for c in (400, 900, 2000, 4500)]
    pos = t / length if rising else 1 - t / length
    out = np.zeros(n)
    for i, b in enumerate(bands):
        w = np.clip(1 - abs(pos * 3 - i), 0, 1)
        out += b * w
    shape = np.sin(np.pi * np.clip(t / length, 0, 1)) ** 2
    return out * shape * 0.9


def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 500 + 900 * (t / 0.09)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)


def key_click():
    n = int(0.035 * SR)
    t = np.arange(n) / SR
    return fft_filter(rng.standard_normal(n), 2000, 9000) * np.exp(-t * 160) * 0.6 + \
        np.sin(2 * np.pi * 180 * t) * np.exp(-t * 120) * 0.3


def ding():
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    out = sum(a * np.sin(2 * np.pi * 1318.5 * r * t) * np.exp(-t * d)
              for r, a, d in ((1, 1, 3), (2.76, .35, 6), (5.4, .15, 10)))
    out += sum(a * np.sin(2 * np.pi * 1760 * r * t) * np.exp(-t * d) * (t > .09)
               for r, a, d in ((1, .8, 3), (2.76, .3, 6)))
    return out * 0.35


def hit():
    k = kick(0.6, 1.4)
    n = len(k)
    t = np.arange(n) / SR
    return k + fft_filter(rng.standard_normal(n), 300, 6000) * np.exp(-t * 14) * 0.5


def impact():
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t * 10)) / SR) * np.exp(-t * 1.6)
    crash = fft_filter(rng.standard_normal(n), 3000) * np.exp(-t * 2.2) * 0.45
    return np.tanh((boom * 1.6 + crash) * 1.2)


def riser(length=1.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = 200 * 2 ** (3 * t / length)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (whoosh(length, True) * 0.8 + tone) * (t / length) ** 2


def crunch():
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for _ in range(38):
        s = rng.uniform(0, 0.45)
        i = int(s * SR)
        m = int(0.012 * SR)
        g = rng.uniform(0.3, 1) * np.exp(-s * 4)
        out[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 5)) * g
    thump = np.concatenate([kick(0.3, 1.3), np.zeros(n - int(0.3 * SR))])
    return fft_filter(out, 900, 10000) * 1.4 + thump * 0.7


SFX = {
    'whoosh': lambda c: whoosh(c.get('dur', 0.6)), 'pop': lambda c: pop(), 'key': lambda c: key_click(),
    'ding': lambda c: ding(), 'hit': lambda c: hit(), 'impact': lambda c: impact(),
    'riser': lambda c: riser(c.get('dur', 1.2)), 'crunch': lambda c: crunch(),
}
SFX_GAIN = {'whoosh': .55, 'pop': .45, 'key': .35, 'ding': .6, 'hit': .8, 'impact': .9, 'riser': .5, 'crunch': .9}


# ---------------------------------------------------------------- arrangements
def music(style, bpm, duration):
    buf = np.zeros((int((duration + 3) * SR), 2))
    beat = 60 / bpm
    bars = int(duration / (4 * beat)) + 2

    if style == 'chill':
        prog = [(57, [57, 60, 64, 67]), (50, [53, 57, 60, 64]), (55, [55, 59, 62, 65]), (48, [52, 55, 59, 64])]
        for b in range(bars):
            t0 = b * 4 * beat
            root, ch = prog[b % 4]
            add(buf, keys([note(n) for n in ch], 4 * beat, 0.6, 0.15), t0, 0.5)
            add(buf, bass(note(root - 12), 1.5 * beat), t0, 0.45)
            add(buf, bass(note(root - 12), 0.8 * beat), t0 + 2.5 * beat, 0.4)
            for k in (0, 2.5):
                add(buf, kick(0.4, 0.8), t0 + k * beat, 0.7)
            for s in (1, 3):
                add(buf, snare(0.25, 170), t0 + s * beat, 0.35)
            for h in range(8):
                swing = 0.08 * beat if h % 2 else 0
                add(buf, hat(), t0 + h * beat / 2 + swing, 0.18 if h % 2 else 0.25, pan=0.3)
    elif style == 'trap':
        prog = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]
        melody = [69, 72, 76, 74, 72, 69, 67, 69]
        for b in range(bars):
            t0 = b * 4 * beat
            root, ch = prog[b % 4]
            add(buf, pad([note(n) for n in ch], 4 * beat), t0, 0.35)
            for k in (0, 1.5, 2.75):
                add(buf, kick(0.3, 1.2), t0 + k * beat, 0.6)
            add(buf, bass(note(root - 12), 1.4 * beat, sub=True), t0, 0.75)
            add(buf, bass(note(root - 12), 1.0 * beat, sub=True), t0 + 1.5 * beat, 0.6)
            add(buf, clap(), t0 + 2 * beat, 0.55)
            add(buf, snare(0.2, 220), t0 + 2 * beat, 0.25)
            steps = 16 if b % 2 == 0 else 14
            for h in range(steps):
                add(buf, hat(), t0 + h * beat / 4, 0.16 if h % 2 else 0.22, pan=0.25)
            if b % 2:
                for r in range(6):
                    add(buf, hat(), t0 + 3.5 * beat + r * beat / 12, 0.14, pan=0.25)
            for i, m in enumerate(melody):
                add(buf, pluck(note(m + (0 if b % 4 < 2 else -2))), t0 + i * beat / 2, 0.22, pan=-0.2)
    else:  # upbeat
        prog = [(48, [60, 64, 67]), (55, [59, 62, 67]), (57, [60, 64, 69]), (53, [60, 65, 69])]
        for b in range(bars):
            t0 = b * 4 * beat
            root, ch = prog[b % 4]
            for q in range(4):
                add(buf, kick(0.35, 1.0), t0 + q * beat, 0.65)
                add(buf, hat(True), t0 + (q + 0.5) * beat, 0.18, pan=0.3)
                add(buf, keys([note(n) for n in ch], 0.45 * beat, 1.0), t0 + (q + 0.5) * beat, 0.45)
                add(buf, bass(note(root - 12), 0.4 * beat), t0 + (q + 0.5) * beat, 0.5)
            for s in (1, 3):
                add(buf, clap(), t0 + s * beat, 0.4)
            for h in range(16):
                add(buf, hat(), t0 + h * beat / 4, 0.08, pan=-0.3)
            add(buf, pad([note(n + 12) for n in ch], 4 * beat), t0, 0.15)
    return buf


def main():
    cues = json.load(open(sys.argv[1]))
    dur = cues['duration']
    mus = music(cues.get('style', 'chill'), cues.get('bpm', 100), dur)
    fx = np.zeros_like(mus)
    for c in cues.get('sfx', []):
        sig = SFX[c['type']](c)
        add(fx, sig, c['t'], SFX_GAIN[c['type']] * c.get('gain', 1))
    n = int(dur * SR)
    mus, fx = mus[:n], fx[:n]
    mus /= max(np.abs(mus).max(), 1e-6)
    t = np.arange(n) / SR
    fade = np.clip((dur - t) / 1.2, 0, 1)[:, None] * np.clip(t / 0.05, 0, 1)[:, None]
    mix = mus * 0.55 * fade + fx * 0.75
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix /= max(np.abs(mix).max(), 1e-6) / 0.93
    pcm = (mix * 32767).astype('<i2')
    with wave.open(sys.argv[2], 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == '__main__':
    main()
