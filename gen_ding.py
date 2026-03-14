import numpy as np
from scipy.io import wavfile
import os

def generate_ding(filename, duration=1.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Sine wave (around 880Hz or 1760Hz)
    frequency = 880
    wave = np.sin(2 * np.pi * frequency * t)
    # Exponential decay
    decay = np.exp(-5 * t)
    ding = wave * decay
    # Normalize
    ding = (ding / np.max(np.abs(ding)) * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, ding)
    print(f"Generated ding: {filename}")

if __name__ == "__main__":
    assets_dir = r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets"
    os.makedirs(assets_dir, exist_ok=True)
    generate_ding(os.path.join(assets_dir, "ding.wav"))
