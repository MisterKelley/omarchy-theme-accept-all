#!/usr/bin/env python3
"""ACCEPT ALL — UI sound set, synthesized. stdlib only (wave + math).

Terminal character: typewriter ticks, square-ish phosphor blips, a power-up
unlock, and a whisper-quiet CRT hum for the ambient bed. Same file names the
arc.sound plugin expects, so the whole desktop speaks the brand while the
theme is active.

    python3 tools/generate_sounds.py
"""
import math
import os
import random
import struct
import wave

RATE = 48000
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sounds")

# Brand notes: E minor pentatonic-ish, phosphor register.
E5, G5, A5, B5, D6, E6, G6, B6, E7 = 659.3, 784.0, 880.0, 987.8, 1174.7, 1318.5, 1568.0, 1975.5, 2637.0


def write(name, samples):
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples))
    print(f"  {name}.wav  {len(samples)/RATE:.2f}s")


def silence(sec):
    return [0.0] * int(RATE * sec)


def tone(freq, sec, vol=0.5, decay=6.0, attack=0.004, square=0.25):
    """A phosphor blip: sine plus a dash of 3rd harmonic, exponential decay."""
    n = int(RATE * sec)
    out = []
    for i in range(n):
        t = i / RATE
        env = min(1.0, t / attack) * math.exp(-decay * t)
        s = math.sin(2 * math.pi * freq * t) + square * math.sin(2 * math.pi * freq * 3 * t) / 3
        out.append(vol * env * s)
    return out


def tick(sec=0.02, vol=0.25, seed=1):
    """Typewriter key: a filtered noise burst with a hard attack."""
    rng = random.Random(seed)
    n = int(RATE * sec)
    out, prev = [], 0.0
    for i in range(n):
        env = math.exp(-28.0 * i / n)
        prev = 0.6 * prev + 0.4 * (rng.random() * 2 - 1)  # one-pole lowpass
        out.append(vol * env * prev)
    return out


def mix(*layers):
    n = max(len(l) for l in layers)
    return [sum(l[i] if i < len(l) else 0.0 for l in layers) for i in range(n)]


def seq(*parts):
    out = []
    for p in parts:
        out += p
    return out


def main():
    os.makedirs(OUT, exist_ok=True)

    # taps and selections: key ticks with a hint of pitch
    write("ui-tap", mix(tick(seed=2), tone(E6, 0.05, vol=0.10, decay=40)))
    write("ui-select", mix(tick(seed=3, vol=0.18), tone(G6, 0.09, vol=0.22, decay=22)))
    write("ui-back", mix(tick(seed=4, vol=0.18), tone(A5, 0.09, vol=0.20, decay=22)))
    write("focus", tone(B5, 0.045, vol=0.10, decay=42))

    # windows print on, clear off
    write("window-open", seq(tick(seed=5, vol=0.2), mix(tone(A5, 0.07, vol=0.2, decay=22), seq(silence(0.045), tone(E6, 0.1, vol=0.24, decay=18)))))
    write("window-close", seq(tick(seed=6, vol=0.18), mix(tone(E6, 0.06, vol=0.2, decay=24), seq(silence(0.04), tone(A5, 0.1, vol=0.2, decay=18)))))

    # workspace: three fast ascending keys — carriage return energy
    write("workspace", seq(mix(tick(seed=7, vol=0.14), tone(E5, 0.05, vol=0.16, decay=26)), mix(tick(seed=8, vol=0.14), tone(A5, 0.05, vol=0.16, decay=26)), mix(tick(seed=9, vol=0.14), tone(E6, 0.09, vol=0.2, decay=20))))

    # notify: the till's little sibling; alert: amber warble
    write("notify", seq(tone(E6, 0.08, vol=0.26, decay=16), silence(0.03), tone(B6, 0.14, vol=0.24, decay=12)))
    write("alert", seq(tone(B5, 0.1, vol=0.3, decay=10), tone(D6, 0.1, vol=0.3, decay=10), tone(B5, 0.1, vol=0.3, decay=10), tone(D6, 0.16, vol=0.3, decay=9)))

    # lock: power-down; unlock: power-up ending on the "accepted" blip
    write("lock", seq(tone(E6, 0.1, vol=0.24, decay=12), tone(B5, 0.1, vol=0.22, decay=12), tone(E5, 0.22, vol=0.2, decay=8)))
    write("unlock", seq(tone(E5, 0.07, vol=0.18, decay=18), tone(B5, 0.07, vol=0.2, decay=18), tone(E6, 0.07, vol=0.22, decay=18), silence(0.03), mix(tick(seed=10, vol=0.16), tone(E7, 0.14, vol=0.22, decay=12))))

    # theme-switch: boot chirp
    write("theme-switch", seq(tone(E5, 0.08, vol=0.2, decay=14), tone(G5, 0.08, vol=0.2, decay=14), tone(B5, 0.08, vol=0.2, decay=14), tone(E6, 0.12, vol=0.24, decay=10), silence(0.05), tone(B6, 0.18, vol=0.2, decay=9)))

    # ambient: whisper-quiet CRT hum, seamless 4s loop (whole periods of 120Hz).
    n = RATE * 4
    rng = random.Random(42)
    bed, prev = [], 0.0
    for i in range(n):
        t = i / RATE
        hum = 0.016 * math.sin(2 * math.pi * 120 * t) + 0.008 * math.sin(2 * math.pi * 240 * t) + 0.004 * math.sin(2 * math.pi * 360 * t)
        prev = 0.985 * prev + 0.015 * (rng.random() * 2 - 1)  # deep-filtered air
        bed.append(hum + 0.01 * prev)
    write("ambient", bed)


if __name__ == "__main__":
    main()
