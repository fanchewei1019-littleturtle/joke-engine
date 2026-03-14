import asyncio
import edge_tts
import json

async def test():
    text = "這是一個測試影片，我們正在研究如何實現動態字幕效果！"
    voice = "zh-TW-HsiaoChenNeural"
    output_file = "test_timing.mp3"
    
    communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    submaker = edge_tts.SubMaker()
    
    # We can get word level timing using events
    word_timings = []
    with open(output_file, "wb") as f:
        async for chunk in communicate.stream():
            print(f"TYPE: {chunk['type']}")
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                print(f"DEBUG: {chunk}")
                word_timings.append(chunk)
                
    for wt in word_timings:
        # offset is in 100ns units (ticks)
        start = wt['offset'] / 10_000_000
        duration = wt['duration'] / 10_000_000
        print(f"Word: {wt['text']}, Start: {start:.3f}s, Duration: {duration:.3f}s")

if __name__ == "__main__":
    asyncio.run(test())
