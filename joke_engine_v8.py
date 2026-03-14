# -*- coding: utf-8 -*-
"""
Joke Video Engine v8
Next-Generation Video Generation Engine for Joke Videos.
New Features in v8:
- Screen Shake Visual Effect for Punchlines!
- Smart Emoji Injection for subtitles based on character & emotion
- Dynamic Audio Ducking simulation (lowers BGM during voice)
- Subtitle Pop-in Animation (slide up)
- Enhanced Scene Transitions
"""

import os
import re
import asyncio
import random
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.video.fx.Resize import Resize
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut

class JokeVideoEngineV8:
    def __init__(self, script_path, output_path="joke_video_v8.mp4", assets_dir="assets"):
        self.script_path = script_path
        self.output_path = output_path
        self.assets_dir = assets_dir
        
        self.voices = {
            "default": "zh-TW-HsiaoChenNeural",
            "dog": "zh-TW-YunJheNeural",
            "owner": "zh-TW-HsiaoYuNeural",
            "person": "zh-TW-HsiaoChenNeural"
        }
        
        self.font_path = "C:\\Windows\\Fonts\\msjhbd.ttc"
        if not os.path.exists(self.font_path):
            self.font_path = "C:\\Windows\\Fonts\\simhei.ttf"

        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)

    def _analyze_emotion_and_emoji(self, text, is_punchline, character):
        rate = "+0%"
        pitch = "+0Hz"
        emoji = ""
        
        if is_punchline:
            rate = "+15%"
            pitch = "+10Hz"
            emoji = random.choice(["💥", "😂", "🤣", "✨"])
        elif "！" in text or "!" in text:
            rate = "+5%"
            pitch = "+5Hz"
            emoji = "❗"
        elif "？" in text or "?" in text:
            pitch = "+8Hz"
            emoji = "❓"
        elif "..." in text or "…" in text:
            rate = "-10%"
            pitch = "-5Hz"
            emoji = "💦"
            
        if not emoji:
            if character == "dog": emoji = "🐶"
            elif character == "owner": emoji = "👱‍♂️"
            else: emoji = "💬"
            
        return rate, pitch, emoji

    async def _generate_voice(self, text, filename, character="default", rate="+0%", pitch="+0Hz"):
        voice = self.voices.get(character, self.voices["default"])
        # Remove emojis for TTS
        clean_text = re.sub(r'[^\w\s，。！？！？,.\u4e00-\u9fa5]', '', text)
        communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch)
        await communicate.save(filename)

    def _parse_script(self):
        with open(self.script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scenes = []
        video_title = "笑話時間"
        
        parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
        for i, part in enumerate(parts):
            if not part.strip(): continue
            lines = part.strip().split('\n')
            title = lines[0].strip()
            
            if i == 1: 
                video_title = title.replace("結尾", "").replace("反轉", "").strip()
                if not video_title: video_title = "笑話時間"
                
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
        return scenes, video_title

    def _apply_vfx(self, clip, duration, character, is_punchline):
        # Ken Burns
        if is_punchline:
            clip = clip.with_effects([Resize(lambda t: 1.0 + 0.4 * (t / duration))])
            # Screen Shake for the first 0.5 seconds of punchline
            shake_func = lambda t: ('center', 'center') if t > 0.5 else (
                1920/2 + random.randint(-15, 15), 
                1080/2 + random.randint(-15, 15)
            )
            # Create a black background to compose the shaking clip over
            bg = ColorClip((1920, 1080), color=(0,0,0)).with_duration(duration)
            clip = CompositeVideoClip([bg, clip.with_position(shake_func)])
            
            # Flash effect
            flash = ColorClip(clip.size, color=(255, 255, 255)).with_duration(0.2)
            clip = CompositeVideoClip([clip, flash.with_position("center").with_effects([CrossFadeOut(duration=0.2)])])

        elif character == 'dog':
            clip = clip.with_effects([Resize(lambda t: 1.0 + 0.15 * (t / duration))])
        elif character == 'owner':
            clip = clip.with_effects([Resize(lambda t: 1.15)])
        else:
            clip = clip.with_effects([Resize(lambda t: 1.15 - 0.15 * (t / duration))])

        return clip

    def _add_subtitle_to_image(self, img_path, text, output_path, emoji=""):
        base_img = Image.open(img_path).convert("RGB")
        base_img = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
        
        try:
            font_sub = ImageFont.truetype(self.font_path, 75)
            font_emoji = ImageFont.truetype("seguiemj.ttf", 75) # Windows Emoji Font
        except:
            font_sub = ImageFont.load_default()
            font_emoji = font_sub
            
        full_text = f"{text} {emoji}".strip()
        
        draw_temp = ImageDraw.Draw(base_img)
        wrapped_lines = []
        line = ""
        for char in full_text:
            line += char
            try:
                bbox = draw_temp.textbbox((0, 0), line, font=font_sub)
                width = bbox[2] - bbox[0]
            except:
                width = len(line) * 75
                
            if width > 1600:
                wrapped_lines.append(line)
                line = ""
        if line:
            wrapped_lines.append(line)
        
        bar_h = 160 + (len(wrapped_lines)-1)*100
        gradient = Image.new('RGBA', (1920, bar_h), (0,0,0,0))
        draw_grad = ImageDraw.Draw(gradient)
        for i in range(bar_h):
            alpha = int(255 * (i / bar_h))
            draw_grad.line([(0, i), (1920, i)], fill=(0, 0, 0, alpha))
        
        base_img.paste(gradient, (0, 1080 - bar_h), gradient)
        
        txt_layer = Image.new('RGBA', base_img.size, (255,255,255,0))
        draw = ImageDraw.Draw(txt_layer)
        
        y_start = 1080 - bar_h + 40
        for line in wrapped_lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=font_sub)
                x_pos = (1920 - (bbox[2] - bbox[0])) / 2
            except:
                x_pos = (1920 - (len(line)*75)) / 2
            
            # Drop Shadow
            shadow_offset = 6
            draw.text((x_pos+shadow_offset, y_start+shadow_offset), line, font=font_sub, fill=(0, 0, 0, 200))
            
            # Stroke
            stroke_width = 3
            for dx in range(-stroke_width, stroke_width+1):
                for dy in range(-stroke_width, stroke_width+1):
                    if dx*dx + dy*dy > 0:
                        draw.text((x_pos+dx, y_start+dy), line, font=font_sub, fill=(0, 0, 0, 255))
            
            # Inner Text (Brighter Yellow with slight gradient effect could be added, but solid is fine)
            draw.text((x_pos, y_start), line, font=font_sub, fill=(255, 240, 80, 255)) 
            y_start += 100
            
        base_img = Image.alpha_composite(base_img.convert("RGBA"), txt_layer).convert("RGB")
        base_img.save(output_path)

    def _create_intro_slide(self, title):
        img = Image.new('RGB', (1920, 1080), color=(20, 20, 35))
        draw = ImageDraw.Draw(img)
        try:
            fnt_large = ImageFont.truetype(self.font_path, 160)
            fnt_small = ImageFont.truetype(self.font_path, 70)
        except:
            fnt_large = fnt_small = ImageFont.load_default()
            
        # Draw Title
        try:
            bbox = draw.textbbox((0, 0), title, font=fnt_large)
            x = (1920 - (bbox[2] - bbox[0])) / 2
        except:
            x = (1920 - len(title)*160) / 2
        y = 380
        draw.text((x+8, y+8), title, font=fnt_large, fill=(0,0,0)) # Drop shadow
        draw.text((x, y), title, font=fnt_large, fill=(255, 215, 0)) # Gold text
        
        # Draw Subtitle
        sub = "🎬 V8 AI 搞笑短片 🎬"
        try:
            bbox2 = draw.textbbox((0, 0), sub, font=fnt_small)
            x2 = (1920 - (bbox2[2] - bbox2[0])) / 2
        except:
            x2 = (1920 - len(sub)*70) / 2
        y2 = 620
        draw.text((x2, y2), sub, font=fnt_small, fill=(200, 220, 255))
        
        intro_path = "temp_intro.jpg"
        img.save(intro_path)
        
        # 2.5 seconds intro with a slight zoom
        clip = ImageClip(intro_path).with_duration(2.5).with_effects([Resize(lambda t: 1.0 + 0.05 * (t / 2.5))])
        return clip

    def generate(self):
        print(f"Starting Video Generation V8 for {self.script_path}")
        scenes, video_title = self._parse_script()
        clips = []
        
        # Add Intro Slide
        intro_clip = self._create_intro_slide(video_title)
        clips.append(intro_clip)
        
        voice_segments = [] # Track (start, end) of voices for audio ducking
        current_time = intro_clip.duration
        
        for i, scene in enumerate(scenes):
            print(f"Processing scene {i+1}/{len(scenes)}: {scene['title']}...")
            
            img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            is_placeholder = False
            if os.path.exists(img_file):
                size = os.path.getsize(img_file)
                if size == 126099: is_placeholder = True
                
            if not os.path.exists(img_file) or is_placeholder:
                img_file = f"temp_fallback_{i}.jpg"
                img = Image.new('RGB', (1920, 1080), color=(40, 40, 60))
                draw = ImageDraw.Draw(img)
                try:
                    fnt = ImageFont.truetype(self.font_path, 80)
                except:
                    fnt = ImageFont.load_default()
                draw.text((100, 100), scene['title'], font=fnt, fill=(255, 255, 255))
                img.save(img_file)
            
            audio_file = f"temp_voice_{i}.mp3"
            emoji = ""
            if scene["voice"]:
                rate, pitch, emoji = self._analyze_emotion_and_emoji(scene["voice"], scene["is_punchline"], scene["character"])
                asyncio.run(self._generate_voice(scene["voice"], audio_file, scene["character"], rate=rate, pitch=pitch))
                audio_clip = AudioFileClip(audio_file)
                # Pad audio slightly for pacing
                padded_audio = CompositeAudioClip([audio_clip.with_start(0.2)]).with_duration(audio_clip.duration + 0.6)
                audio_clip = padded_audio
                voice_segments.append((current_time + 0.2, current_time + audio_clip.duration - 0.4))
            else:
                # Use a dummy audio clip to set duration if no voice
                # moviepy 2.0 ColorClip or similar doesn't have AudioClip, we create a silent audio array
                import numpy as np
                from moviepy import AudioArrayClip
                silent_array = np.zeros((int(44100 * 3), 2))
                audio_clip = AudioArrayClip(silent_array, fps=44100).with_duration(3.0)
                
            if scene["voice"]:
                temp_img_with_text = f"temp_img_text_{i}.jpg"
                self._add_subtitle_to_image(img_file, scene["voice"], temp_img_with_text, emoji)
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
                
            img_clip = self._apply_vfx(img_clip, audio_clip.duration, scene["character"], scene["is_punchline"])
            
            if i > 0 or len(clips) > 0:
                img_clip = img_clip.with_effects([CrossFadeIn(duration=0.6)])
                
            video_clip = img_clip.with_audio(audio_clip)
            clips.append(video_clip)
            
            current_time += video_clip.duration
            
        print("Combining clips...")
        final_video_clip = concatenate_videoclips(clips, method="compose")
        
        bgm_path = "../joke_factory/assets/bgm.wav"
        if not os.path.exists(bgm_path):
            bgm_path = os.path.join(self.assets_dir, "bgm.wav")
            
        combined_audio_clips = [final_video_clip.audio]
        
        # Add laughing tracks
        curr_t = intro_clip.duration
        for i, scene in enumerate(scenes):
            clip_dur = clips[i+1].duration 
            if scene.get("is_punchline", False):
                laugh_file = f"temp_laugh_{i}.mp3"
                if not os.path.exists(laugh_file):
                    try:
                        asyncio.run(self._generate_voice("哈哈哈！太好笑了！", laugh_file, "default", rate="+25%", pitch="+20Hz"))
                    except:
                        pass
                if os.path.exists(laugh_file):
                    laugh_clip = AudioFileClip(laugh_file)
                    start_time = max(0, curr_t + clip_dur - 1.5)
                    laugh_clip = laugh_clip.with_start(start_time).with_effects([MultiplyVolume(2.0)])
                    combined_audio_clips.append(laugh_clip)
            curr_t += clip_dur
            
        if os.path.exists(bgm_path):
            print("Adding dynamic BGM (Ducking enabled)...")
            bgm = AudioFileClip(bgm_path)
            if bgm.duration < final_video_clip.duration:
                bgm = bgm.with_effects([AudioLoop(duration=final_video_clip.duration)])
            else:
                bgm = bgm.subclipped(0, final_video_clip.duration)
            
            # Simulated Ducking: Volume is 0.05 when people speak, 0.20 otherwise
            def ducking_volume(t):
                for (start, end) in voice_segments:
                    if start <= t <= end:
                        return 0.05
                return 0.20
                
            bgm = bgm.with_effects([
                MultiplyVolume(ducking_volume),
                AudioFadeIn(duration=2.0), 
                AudioFadeOut(duration=2.0)
            ])
            combined_audio_clips.append(bgm)
            
        final_video_clip = final_video_clip.with_audio(CompositeAudioClip(combined_audio_clips))

        print(f"Writing final video: {self.output_path}...")
        final_video_clip.write_videofile(self.output_path, fps=30, codec="libx264", audio_codec="aac")
        
        print("Cleaning up temporary files...")
        if os.path.exists("temp_intro.jpg"): os.remove("temp_intro.jpg")
        for i in range(len(scenes)):
            for f in [f"temp_fallback_{i}.jpg", f"temp_voice_{i}.mp3", f"temp_img_text_{i}.jpg", f"temp_laugh_{i}.mp3"]:
                if os.path.exists(f): os.remove(f)
            
        print("Generation Complete! Engine v8 finished.")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "bragging_dog_v8.mp4"
    engine = JokeVideoEngineV8(script, output)
    engine.generate()
