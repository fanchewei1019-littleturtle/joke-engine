import numpy as np
import wave
import struct
import os

def generate_shake_rumble(filename, duration=1.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Low frequency rumble: 30-80 Hz
    rumble = np.sin(2 * np.pi * 50 * t) * 0.5 + np.sin(2 * np.pi * 35 * t) * 0.3
    # Add some noise
    noise = np.random.uniform(-0.1, 0.1, len(t))
    # Envelope
    envelope = np.ones(len(t))
    fade_len = int(sample_rate * 0.2)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    shake = (rumble + noise) * envelope
    # Normalize
    shake = (shake / np.max(np.abs(shake)) * 28000).astype(np.int16)
    
    # Save using wave module
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        # Struct.pack to binary
        for val in shake:
            data = struct.pack('<h', int(val))
            wav.writeframesraw(data)
    print(f"Generated shake rumble: {filename}")

if __name__ == "__main__":
    assets_dir = r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets"
    os.makedirs(assets_dir, exist_ok=True)
    generate_shake_rumble(os.path.join(assets_dir, "shake.wav"))
