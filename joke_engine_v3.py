# -*- coding: utf-8 -*-
import os
import re
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip
from moviepy.audio.AudioClip import AudioClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.Resize import Resize
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop

# Voice mapping for different characters
VOICES = {
    "default": "zh-TW-HsiaoChenNeural", # Female/Neutral Narrator
    "dog": "zh-TW-YunJheNeural",        # Male
    "owner": "zh-TW-YunJheNeural",      # Male
    "person": "zh-TW-HsiaoChenNeural"   # Female/Neutral
}

async def generate_voice_edge(text, filename, character="default"):
    voice = VOICES.get(character, VOICES["default"])
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def parse_markdown_v3(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scenes = []
    # Split by ## headers
    parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
    for part in parts:
        if not part.strip(): continue
        lines = part.strip().split('\n')
        title = lines[0].strip()
        voice_text = []
        image_desc = ""
        character = "default"
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- **畫面**'):
                image_desc = line.replace('- **畫面**：', '').strip()
            elif line.startswith('- **旁白**'):
                voice_text.append(line.replace('- **旁白**：', '').strip())
                # If there's a character dialogue, keep that character, else default
            elif line.startswith('- **狗狗**'):
                voice_text.append(line.replace('- **狗狗**', '').strip())
                character = "dog"
            elif line.startswith('- **屋主**'):
                voice_text.append(line.replace('- **屋主**：', '').strip())
                character = "owner"
            elif line.startswith('- **文字**'):
                image_desc += " " + line.replace('- **文字**：', '').strip()
        
        combined_voice = " ".join(voice_text)
        if combined_voice or image_desc:
            scenes.append({
                "title": title,
                "voice": combined_voice,
                "image_desc": image_desc,
                "character": character
            })
    return scenes

def create_video_v3(script_path, output_filename="joke_video_v3.mp4"):
    # ... rest of code ...
    scenes = parse_markdown_v3(script_path)
    clips = []
    assets_dir = "assets"
    
    # Ensure Assets Directory exists
    if not os.path.exists(assets_dir): os.makedirs(assets_dir)

    font_path = "C:\\Windows\\Fonts\\msjhbd.ttc" # Microsoft JhengHei Bold
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\simhei.ttf"

    for i, scene in enumerate(scenes):
        print(f"Processing scene {i+1}/{len(scenes)}: {scene['title']}...")
        
        # 1. Determine image
        img_file = os.path.join(assets_dir, f"scene_{i+1}.jpg")
        # Placeholder check (size should be > 130000 or different from others)
        is_placeholder = False
        if os.path.exists(img_file):
            size = os.path.getsize(img_file)
            if size == 126099: is_placeholder = True # Known placeholder size
            
        if not os.path.exists(img_file) or is_placeholder:
            print(f"Asset {img_file} is missing or placeholder. Using generated text slide.")
            img_file = f"temp_fallback_{i}.jpg"
            # Basic fallback generation (simpler than engine v2 for speed)
            img = Image.new('RGB', (1920, 1080), color=(30, 30, 30))
            img.save(img_file)
        
        # 2. Generate Audio with edge-tts
        audio_file = f"temp_voice_{i}.mp3"
        if scene["voice"]:
            asyncio.run(generate_voice_edge(scene["voice"], audio_file, scene["character"]))
            audio_clip = AudioFileClip(audio_file)
        else:
            # Create a 3-second silent audio clip
            audio_clip = AudioClip(lambda t: 0, duration=3)
            
        # 3. Create Video Clip
        img_clip = ImageClip(img_file).with_duration(audio_clip.duration)
        
        # Ensure image is 1920x1080
        img_clip = img_clip.with_effects([Resize(height=1080)])
        w, h = img_clip.size
        if w > 1920:
            img_clip = img_clip.cropped(x_center=w/2, y_center=h/2, width=1920, height=1080)
        else:
            # Letterbox if too small
            bg = ColorClip((1920, 1080), color=(0,0,0)).with_duration(audio_clip.duration)
            img_clip = CompositeVideoClip([bg, img_clip.with_position("center")])
            
        # Add a subtle zoom effect (Ken Burns)
        # Zoom from 1.0 to 1.1 over the duration
        img_clip = img_clip.with_effects([Resize(lambda t: 1.0 + 0.1 * (t / audio_clip.duration))])
        
        # 4. Add Subtitles (Captions)
        if scene["voice"]:
            # Simple text overlay
            # Note: TextClip requires ImageMagick or we can use a custom function to draw on frames
            # To avoid ImageMagick dependency, we'll use a trick: 
            # We'll use a function to modify the image clip frames if needed.
            # But let's try the Pillow approach for simplicity on each clip
            
            # Since MoviePy TextClip is tricky on Windows without ImageMagick,
            # I will draw the subtitle directly on the image for this scene
            temp_img_with_text = f"temp_img_text_{i}.jpg"
            base_img = Image.open(img_file).convert("RGB")
            base_img = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(base_img)
            
            try:
                font_sub = ImageFont.truetype(font_path, 60)
            except:
                font_sub = ImageFont.load_default()
            
            # Draw semi-transparent shadow/box
            text = scene["voice"]
            # Wrap text manually
            wrapped_lines = []
            line = ""
            for char in text:
                line += char
                bbox = draw.textbbox((0, 0), line, font=font_sub)
                if bbox[2] - bbox[0] > 1600:
                    wrapped_lines.append(line)
                    line = ""
            wrapped_lines.append(line)
            
            # Draw black bar at bottom
            bar_h = 100 + (len(wrapped_lines)-1)*70
            draw.rectangle([0, 1080-bar_h, 1920, 1080], fill=(0, 0, 0, 180))
            
            y_start = 1080 - bar_h + 20
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font_sub)
                x_pos = (1920 - (bbox[2] - bbox[0])) / 2
                draw.text((x_pos, y_start), line, font=font_sub, fill=(255, 255, 255))
                y_start += 70
                
            base_img.save(temp_img_with_text)
            img_clip = ImageClip(temp_img_with_text).with_duration(audio_clip.duration)

        if i > 0:
            img_clip = img_clip.with_effects([CrossFadeIn(duration=0.5)])
            
        video_clip = img_clip.with_audio(audio_clip)
        clips.append(video_clip)
        
    print("Combining clips...")
    final_video_clip = concatenate_videoclips(clips, method="compose")
    
    bgm_path = "../joke_factory/assets/bgm.wav"
    if os.path.exists(bgm_path):
        print("Adding background music...")
        bgm = AudioFileClip(bgm_path).with_effects([MultiplyVolume(0.15)])
        if bgm.duration < final_video_clip.duration:
            bgm = bgm.with_effects([AudioLoop(duration=final_video_clip.duration)])
        else:
            bgm = bgm.subclipped(0, final_video_clip.duration)
            
        combined_audio = CompositeAudioClip([final_video_clip.audio, bgm])
        final_video_clip = final_video_clip.with_audio(combined_audio)

    print(f"Writing final video: {output_filename}...")
    final_video_clip.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup
    for i in range(len(scenes)):
        for f in [f"temp_fallback_{i}.jpg", f"temp_voice_{i}.mp3", f"temp_img_text_{i}.jpg"]:
            if os.path.exists(f): os.remove(f)
        
    print("Done!")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "bragging_dog_v3.mp4"
    create_video_v3(script, output)
