import numpy as np
from scipy.io import wavfile
import os

def generate_whoosh(filename, duration=0.8, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    # White noise
    noise = np.random.uniform(-1, 1, len(t))
    # Parabolic envelope for volume: (t-0.4)^2 peak at 0.4
    # Peak should be at 1.0, sides at 0.0
    # Center = duration / 2
    center = duration / 2
    envelope = np.exp(-((t - center)**2) / (2 * (0.15**2)))
    
    whoosh = noise * envelope
    # Smooth fade in/out
    fade_len = int(sample_rate * 0.1)
    whoosh[:fade_len] *= np.linspace(0, 1, fade_len)
    whoosh[-fade_len:] *= np.linspace(1, 0, fade_len)
    
    # Normalize
    whoosh = (whoosh / np.max(np.abs(whoosh)) * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, whoosh)
    print(f"Generated whoosh: {filename}")

if __name__ == "__main__":
    assets_dir = r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets"
    os.makedirs(assets_dir, exist_ok=True)
    generate_whoosh(os.path.join(assets_dir, "whoosh.wav"))
