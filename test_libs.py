import edge_tts
import asyncio
import moviepy
import os

async def test_tts():
    print("Testing edge-tts...", flush=True)
    communicate = edge_tts.Communicate("你好，我是小烏龜。", "zh-TW-HsiaoChenNeural")
    await communicate.save("test_voice.mp3")
    print("edge-tts OK.", flush=True)

def test_moviepy():
    print("Testing moviepy...", flush=True)
    from moviepy import ColorClip
    clip = ColorClip((640, 480), color=(255, 0, 0)).with_duration(2)
    clip.write_videofile("test_video.mp4", fps=24, codec="libx264")
    print("moviepy OK.", flush=True)

if __name__ == "__main__":
    asyncio.run(test_tts())
    test_moviepy()
