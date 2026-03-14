# -*- coding: utf-8 -*-
"""
Joke Video Engine v6
Advanced Video Generation Engine for Joke Videos.
Features:
- Object-Oriented Design
- Character-specific Ken Burns effects for better storytelling
- Advanced subtitle rendering with thick outline strokes
- Improved sound effect injection for punchlines
- Better BGM mixing
"""

import os
import re
import asyncio
import random
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip
from moviepy.audio.AudioClip import AudioClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.Resize import Resize
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop

class JokeVideoEngine:
    def __init__(self, script_path, output_path="joke_video_v6.mp4", assets_dir="assets"):
        self.script_path = script_path
        self.output_path = output_path
        self.assets_dir = assets_dir
        
        self.voices = {
            "default": "zh-TW-HsiaoChenNeural",
            "dog": "zh-TW-YunJheNeural",
            "owner": "zh-TW-HsiaoYuNeural",
            "person": "zh-TW-HsiaoChenNeural"
        }
        
        # System font logic for Windows
        self.font_path = "C:\\Windows\\Fonts\\msjhbd.ttc"
        if not os.path.exists(self.font_path):
            self.font_path = "C:\\Windows\\Fonts\\simhei.ttf"

        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)

    async def _generate_voice(self, text, filename, character="default", rate="+0%", pitch="+0Hz"):
        voice = self.voices.get(character, self.voices["default"])
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(filename)

    def _parse_script(self):
        with open(self.script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scenes = []
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
                elif line.startswith('- **狗狗**'):
                    voice_text.append(line.replace('- **狗狗**：', '').replace('- **狗狗**', '').strip())
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
                    "character": character,
                    "is_punchline": "結尾" in title or "反轉" in title
                })
        return scenes

    def _apply_character_ken_burns(self, clip, duration, character, is_punchline):
        if is_punchline:
            # Dramatic fast zoom-in for punchline
            return clip.with_effects([Resize(lambda t: 1.0 + 0.3 * (t / duration))])
        
        if character == 'dog':
            # Slight zoom in for the dog
            return clip.with_effects([Resize(lambda t: 1.0 + 0.15 * (t / duration))])
        elif character == 'owner':
            # Pan right for the owner
            return clip.with_effects([Resize(lambda t: 1.2)]).with_position(lambda t: ('center', 'center'))
        else:
            # Slow zoom out for narration
            return clip.with_effects([Resize(lambda t: 1.15 - 0.15 * (t / duration))])

    def _add_subtitle_to_image(self, img_path, text, output_path):
        base_img = Image.open(img_path).convert("RGB")
        base_img = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(base_img)
        
        try:
            font_sub = ImageFont.truetype(self.font_path, 65)
        except:
            font_sub = ImageFont.load_default()
        
        # Wrap text
        wrapped_lines = []
        line = ""
        for char in text:
            line += char
            bbox = draw.textbbox((0, 0), line, font=font_sub)
            if bbox[2] - bbox[0] > 1500:
                wrapped_lines.append(line)
                line = ""
        if line:
            wrapped_lines.append(line)
        
        bar_h = 120 + (len(wrapped_lines)-1)*80
        # Create a gradient overlay for text readability instead of solid box
        gradient = Image.new('RGBA', (1920, bar_h), (0,0,0,0))
        draw_grad = ImageDraw.Draw(gradient)
        for i in range(bar_h):
            alpha = int(220 * (i / bar_h))
            draw_grad.line([(0, i), (1920, i)], fill=(0, 0, 0, alpha))
        
        base_img.paste(gradient, (0, 1080 - bar_h), gradient)
        draw = ImageDraw.Draw(base_img)
        
        y_start = 1080 - bar_h + 30
        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font_sub)
            x_pos = (1920 - (bbox[2] - bbox[0])) / 2
            
            # Thick stroke (8 directions)
            stroke_width = 3
            for dx in range(-stroke_width, stroke_width+1):
                for dy in range(-stroke_width, stroke_width+1):
                    if dx*dx + dy*dy > 0:
                        draw.text((x_pos+dx, y_start+dy), line, font=font_sub, fill=(0, 0, 0))
            
            # Inner text
            draw.text((x_pos, y_start), line, font=font_sub, fill=(255, 220, 0)) # Golden yellow text
            y_start += 80
            
        base_img.save(output_path)

    def generate(self):
        print(f"Starting Video Generation V6 for {self.script_path}")
        scenes = self._parse_script()
        clips = []
        
        for i, scene in enumerate(scenes):
            print(f"Processing scene {i+1}/{len(scenes)}: {scene['title']}...")
            
            img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            is_placeholder = False
            if os.path.exists(img_file):
                size = os.path.getsize(img_file)
                if size == 126099: is_placeholder = True
                
            if not os.path.exists(img_file) or is_placeholder:
                print(f"Asset {img_file} missing. Generating fallback.")
                img_file = f"temp_fallback_{i}.jpg"
                img = Image.new('RGB', (1920, 1080), color=(50, 50, 80))
                # Add scene title to fallback image
                draw = ImageDraw.Draw(img)
                try:
                    fnt = ImageFont.truetype(self.font_path, 80)
                except:
                    fnt = ImageFont.load_default()
                draw.text((100, 100), scene['title'], font=fnt, fill=(255, 255, 255))
                img.save(img_file)
            
            audio_file = f"temp_voice_{i}.mp3"
            if scene["voice"]:
                # If punchline, make voice slightly faster and higher pitched
                rate = "+10%" if scene["is_punchline"] else "+0%"
                pitch = "+5Hz" if scene["is_punchline"] else "+0Hz"
                asyncio.run(self._generate_voice(scene["voice"], audio_file, scene["character"], rate=rate, pitch=pitch))
                audio_clip = AudioFileClip(audio_file)
            else:
                audio_clip = AudioClip(lambda t: 0, duration=3)
                
            if scene["voice"]:
                temp_img_with_text = f"temp_img_text_{i}.jpg"
                self._add_subtitle_to_image(img_file, scene["voice"], temp_img_with_text)
                img_clip = ImageClip(temp_img_with_text).with_duration(audio_clip.duration)
            else:
                img_clip = ImageClip(img_file).with_duration(audio_clip.duration)
                
            img_clip = img_clip.with_effects([Resize(height=1080)])
            w, h = img_clip.size
            if w > 1920:
                img_clip = img_clip.cropped(x_center=w/2, y_center=h/2, width=1920, height=1080)
            else:
                bg = ColorClip((1920, 1080), color=(0,0,0)).with_duration(audio_clip.duration)
                img_clip = CompositeVideoClip([bg, img_clip.with_position("center")])
                
            # Apply character specific Ken Burns
            img_clip = self._apply_character_ken_burns(img_clip, audio_clip.duration, scene["character"], scene["is_punchline"])
            
            # Apply transition
            if i > 0:
                img_clip = img_clip.with_effects([CrossFadeIn(duration=0.5)])
                
            video_clip = img_clip.with_audio(audio_clip)
            clips.append(video_clip)
            
        print("Combining clips...")
        final_video_clip = concatenate_videoclips(clips, method="compose")
        
        # Audio Mixing: BGM + Punchline SFX
        bgm_path = "../joke_factory/assets/bgm.wav"
        combined_audio_clips = [final_video_clip.audio]
        
        current_time = 0
        for i, scene in enumerate(scenes):
            clip_dur = clips[i].duration
            if scene.get("is_punchline", False):
                laugh_file = f"temp_laugh_{i}.mp3"
                if not os.path.exists(laugh_file):
                    try:
                        # Animated laugh TTS
                        asyncio.run(self._generate_voice("哈哈哈！太好笑了！", laugh_file, "default", rate="+20%", pitch="+15Hz"))
                    except:
                        pass
                if os.path.exists(laugh_file):
                    laugh_clip = AudioFileClip(laugh_file)
                    # Start playing laugh near the end of the clip
                    start_time = max(0, current_time + clip_dur - 1.5)
                    laugh_clip = laugh_clip.with_start(start_time).with_effects([MultiplyVolume(1.5)])
                    combined_audio_clips.append(laugh_clip)
            current_time += clip_dur
            
        if os.path.exists(bgm_path):
            print("Adding background music...")
            bgm = AudioFileClip(bgm_path).with_effects([MultiplyVolume(0.12)]) # Slightly louder BGM
            if bgm.duration < final_video_clip.duration:
                bgm = bgm.with_effects([AudioLoop(duration=final_video_clip.duration)])
            else:
                bgm = bgm.subclipped(0, final_video_clip.duration)
            combined_audio_clips.append(bgm)
            
        final_video_clip = final_video_clip.with_audio(CompositeAudioClip(combined_audio_clips))

        print(f"Writing final video: {self.output_path}...")
        final_video_clip.write_videofile(self.output_path, fps=24, codec="libx264", audio_codec="aac")
        
        # Cleanup
        print("Cleaning up temporary files...")
        for i in range(len(scenes)):
            for f in [f"temp_fallback_{i}.jpg", f"temp_voice_{i}.mp3", f"temp_img_text_{i}.jpg", f"temp_laugh_{i}.mp3"]:
                if os.path.exists(f): os.remove(f)
            
        print("Generation Complete!")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "bragging_dog_v6.mp4"
    engine = JokeVideoEngine(script, output)
    engine.generate()
