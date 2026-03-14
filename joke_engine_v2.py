# -*- coding: utf-8 -*-
import os
import re
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.Resize import Resize

def parse_markdown_v2(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scenes = []
    # Split by ## headers
    parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
    for part in parts:
        if not part.strip(): continue
        lines = part.strip().split('\n')
        title = lines[0].strip()
        voice_text = ""
        image_desc = ""
        prompt = ""
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- **畫面**'):
                image_desc = line.replace('- **畫面**：', '').strip()
            elif line.startswith('- **旁白**'):
                voice_text = line.replace('- **旁白**：', '').strip()
            elif line.startswith('- **狗狗**'):
                voice_text = line.replace('- **狗狗**', '').strip()
            elif line.startswith('- **屋主**'):
                voice_text = line.replace('- **屋主**：', '').strip()
            elif line.startswith('- **文字**'):
                image_desc += " " + line.replace('- **文字**：', '').strip()
            elif line.startswith('- **Image Prompt**'):
                prompt = line.replace('- **Image Prompt**:', '').strip()
        
        if voice_text or image_desc:
            scenes.append({
                "title": title,
                "voice": voice_text,
                "image_desc": image_desc,
                "prompt": prompt
            })
    return scenes

def generate_fallback_image(title, description, filename, avatar_path="../joke_factory/assets/avatar.jpg"):
    size = (1920, 1080)
    img = Image.new('RGB', size, color=(40, 44, 52)) 
    draw = ImageDraw.Draw(img)
    
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\simhei.ttf"
        
    try:
        font_title = ImageFont.truetype(font_path, 80)
        font_desc = ImageFont.truetype(font_path, 50)
    except:
        font_title = ImageFont.load_default()
        font_desc = ImageFont.load_default()

    draw.text((100, 100), title, font=font_title, fill=(255, 215, 0))
    
    # Wrap text
    words = description
    y = 300
    line = ""
    for char in words:
        line += char
        bbox = draw.textbbox((0, 0), line, font=font_desc)
        if bbox[2] - bbox[0] > 1700:
            draw.text((100, y), line, font=font_desc, fill=(255, 255, 255))
            y += 80
            line = ""
    draw.text((100, y), line, font=font_desc, fill=(255, 255, 255))

    img.save(filename)
    return filename

def create_video_v2(script_path, output_filename="joke_video_v2.mp4"):
    scenes = parse_markdown_v2(script_path)
    clips = []
    
    assets_dir = "assets"
    
    for i, scene in enumerate(scenes):
        print(f"Processing scene {i+1}/{len(scenes)}: {scene['title']}...")
        
        # Determine image
        img_file = os.path.join(assets_dir, f"scene_{i+1}.jpg")
        if not os.path.exists(img_file):
            print(f"Asset {img_file} not found, using fallback image.")
            img_file = f"temp_fallback_{i}.jpg"
            generate_fallback_image(scene["title"], scene["image_desc"], img_file)
        
        # Generate Audio
        audio_file = f"temp_voice_{i}.mp3"
        if scene["voice"]:
            tts = gTTS(text=scene["voice"], lang='zh-tw')
            tts.save(audio_file)
            audio_clip = AudioFileClip(audio_file)
        else:
            # Silent clip if no voice
            audio_clip = AudioFileClip("../joke_factory/assets/bgm.wav").subclipped(0, 3).with_effects([MultiplyVolume(0)])
        
        # Create Video Clip
        img_clip = ImageClip(img_file).with_duration(audio_clip.duration)
        
        # Ensure image is 1920x1080
        img_clip = img_clip.with_effects([Resize(height=1080)])
        # Crop to center if width is wrong
        w, h = img_clip.size
        if w > 1920:
            img_clip = img_clip.subclipped(0, audio_clip.duration).cropped(x_center=w/2, y_center=h/2, width=1920, height=1080)
        
        if i > 0:
            img_clip = img_clip.with_effects([CrossFadeIn(duration=0.3)])
            
        video_clip = img_clip.with_audio(audio_clip)
        clips.append(video_clip)
        
    print("Combining clips...")
    final_video_clip = concatenate_videoclips(clips, method="compose")
    
    bgm_path = "../joke_factory/assets/bgm.wav"
    if os.path.exists(bgm_path):
        print("Adding background music...")
        bgm = AudioFileClip(bgm_path).with_effects([MultiplyVolume(0.1)])
        if bgm.duration < final_video_clip.duration:
            bgm = bgm.with_effects([AudioLoop(duration=final_video_clip.duration)])
        else:
            bgm = bgm.subclipped(0, final_video_clip.duration)
            
        combined_audio = CompositeAudioClip([final_video_clip.audio, bgm])
        final_video_clip = final_video_clip.with_audio(combined_audio)

    print(f"Writing final video: {output_filename}...")
    final_video_clip.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # Cleanup temp files
    for i in range(len(scenes)):
        if os.path.exists(f"temp_fallback_{i}.jpg"): os.remove(f"temp_fallback_{i}.jpg")
        if os.path.exists(f"temp_voice_{i}.mp3"): os.remove(f"temp_voice_{i}.mp3")
        
    print("Done!")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "bragging_dog.mp4"
    create_video_v2(script, output)
