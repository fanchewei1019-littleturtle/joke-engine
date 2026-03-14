# -*- coding: utf-8 -*-
"""
Joke Video Engine v7
Next-Generation Video Generation Engine for Joke Videos.
Features:
- Dedicated Intro Title Slide
- Emotion-driven voice modulation (auto pitch/rate based on punctuation)
- Advanced Subtitles with Outline and Drop Shadow
- Punchline Visual Flash Effect
- Smooth BGM Fade-in and Fade-out
"""

import os
import re
import asyncio
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip, VideoClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.video.fx.Resize import Resize
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut

class JokeVideoEngineV7:
    def __init__(self, script_path, output_path="joke_video_v7.mp4", assets_dir="assets"):
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

    def _analyze_emotion(self, text, is_punchline):
        rate = "+0%"
        pitch = "+0Hz"
        
        if is_punchline:
            rate = "+15%"
            pitch = "+10Hz"
        elif "！" in text or "!" in text:
            rate = "+5%"
            pitch = "+5Hz"
        elif "？" in text or "?" in text:
            pitch = "+8Hz"
        elif "..." in text or "…" in text:
            rate = "-10%"
            pitch = "-5Hz"
            
        return rate, pitch

    async def _generate_voice(self, text, filename, character="default", rate="+0%", pitch="+0Hz"):
        voice = self.voices.get(character, self.voices["default"])
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
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
            
            if i == 1: # Assuming first valid part might contain the main title if we wanted to extract it, but let's just use the first scene's title as a base or keep default
                pass
                
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
        elif character == 'dog':
            clip = clip.with_effects([Resize(lambda t: 1.0 + 0.15 * (t / duration))])
        elif character == 'owner':
            clip = clip.with_effects([Resize(lambda t: 1.15)]).with_position(lambda t: ('center', 'center'))
        else:
            clip = clip.with_effects([Resize(lambda t: 1.15 - 0.15 * (t / duration))])

        # Flash effect for punchline
        if is_punchline:
            flash = ColorClip(clip.size, color=(255, 255, 255)).with_duration(0.15)
            # We composite the flash at the start
            clip = CompositeVideoClip([clip, flash.with_position("center").with_effects([CrossFadeOut(duration=0.15)])])

        return clip

    def _add_subtitle_to_image(self, img_path, text, output_path):
        base_img = Image.open(img_path).convert("RGB")
        base_img = base_img.resize((1920, 1080), Image.Resampling.LANCZOS)
        
        try:
            font_sub = ImageFont.truetype(self.font_path, 70)
        except:
            font_sub = ImageFont.load_default()
        
        draw_temp = ImageDraw.Draw(base_img)
        wrapped_lines = []
        line = ""
        for char in text:
            line += char
            bbox = draw_temp.textbbox((0, 0), line, font=font_sub)
            if bbox[2] - bbox[0] > 1500:
                wrapped_lines.append(line)
                line = ""
        if line:
            wrapped_lines.append(line)
        
        bar_h = 140 + (len(wrapped_lines)-1)*90
        gradient = Image.new('RGBA', (1920, bar_h), (0,0,0,0))
        draw_grad = ImageDraw.Draw(gradient)
        for i in range(bar_h):
            alpha = int(240 * (i / bar_h))
            draw_grad.line([(0, i), (1920, i)], fill=(0, 0, 0, alpha))
        
        base_img.paste(gradient, (0, 1080 - bar_h), gradient)
        
        # Text Layer with Drop Shadow and Stroke
        txt_layer = Image.new('RGBA', base_img.size, (255,255,255,0))
        draw = ImageDraw.Draw(txt_layer)
        
        y_start = 1080 - bar_h + 40
        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font_sub)
            x_pos = (1920 - (bbox[2] - bbox[0])) / 2
            
            # Drop Shadow
            shadow_offset = 6
            draw.text((x_pos+shadow_offset, y_start+shadow_offset), line, font=font_sub, fill=(0, 0, 0, 180))
            
            # Thick Stroke
            stroke_width = 3
            for dx in range(-stroke_width, stroke_width+1):
                for dy in range(-stroke_width, stroke_width+1):
                    if dx*dx + dy*dy > 0:
                        draw.text((x_pos+dx, y_start+dy), line, font=font_sub, fill=(0, 0, 0, 255))
            
            # Inner Text (Brighter Yellow)
            draw.text((x_pos, y_start), line, font=font_sub, fill=(255, 235, 59, 255)) 
            y_start += 90
            
        base_img = Image.alpha_composite(base_img.convert("RGBA"), txt_layer).convert("RGB")
        base_img.save(output_path)

    def _create_intro_slide(self, title):
        img = Image.new('RGB', (1920, 1080), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)
        try:
            fnt_large = ImageFont.truetype(self.font_path, 150)
            fnt_small = ImageFont.truetype(self.font_path, 60)
        except:
            fnt_large = fnt_small = ImageFont.load_default()
            
        # Draw Title
        bbox = draw.textbbox((0, 0), title, font=fnt_large)
        x = (1920 - (bbox[2] - bbox[0])) / 2
        y = 400
        draw.text((x+5, y+5), title, font=fnt_large, fill=(0,0,0)) # Shadow
        draw.text((x, y), title, font=fnt_large, fill=(255, 100, 100))
        
        # Draw Subtitle
        sub = "AI 搞笑短片"
        bbox2 = draw.textbbox((0, 0), sub, font=fnt_small)
        x2 = (1920 - (bbox2[2] - bbox2[0])) / 2
        y2 = 600
        draw.text((x2, y2), sub, font=fnt_small, fill=(200, 200, 200))
        
        intro_path = "temp_intro.jpg"
        img.save(intro_path)
        
        # 2 seconds intro
        clip = ImageClip(intro_path).with_duration(2.0)
        return clip

    def generate(self):
        print(f"Starting Video Generation V7 for {self.script_path}")
        scenes, video_title = self._parse_script()
        clips = []
        
        # Add Intro Slide
        intro_clip = self._create_intro_slide(video_title)
        clips.append(intro_clip)
        
        for i, scene in enumerate(scenes):
            print(f"Processing scene {i+1}/{len(scenes)}: {scene['title']}...")
            
            img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            is_placeholder = False
            if os.path.exists(img_file):
                size = os.path.getsize(img_file)
                if size == 126099: is_placeholder = True
                
            if not os.path.exists(img_file) or is_placeholder:
                img_file = f"temp_fallback_{i}.jpg"
                img = Image.new('RGB', (1920, 1080), color=(50, 50, 80))
                draw = ImageDraw.Draw(img)
                try:
                    fnt = ImageFont.truetype(self.font_path, 80)
                except:
                    fnt = ImageFont.load_default()
                draw.text((100, 100), scene['title'], font=fnt, fill=(255, 255, 255))
                img.save(img_file)
            
            audio_file = f"temp_voice_{i}.mp3"
            if scene["voice"]:
                rate, pitch = self._analyze_emotion(scene["voice"], scene["is_punchline"])
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
                
            img_clip = self._apply_vfx(img_clip, audio_clip.duration, scene["character"], scene["is_punchline"])
            
            if i > 0 or len(clips) > 0:
                img_clip = img_clip.with_effects([CrossFadeIn(duration=0.5)])
                
            video_clip = img_clip.with_audio(audio_clip)
            clips.append(video_clip)
            
        print("Combining clips...")
        final_video_clip = concatenate_videoclips(clips, method="compose")
        
        bgm_path = "../joke_factory/assets/bgm.wav"
        combined_audio_clips = [final_video_clip.audio]
        
        current_time = intro_clip.duration
        for i, scene in enumerate(scenes):
            clip_dur = clips[i+1].duration # offset by intro
            if scene.get("is_punchline", False):
                laugh_file = f"temp_laugh_{i}.mp3"
                if not os.path.exists(laugh_file):
                    try:
                        asyncio.run(self._generate_voice("哈哈哈！太好笑了！", laugh_file, "default", rate="+25%", pitch="+20Hz"))
                    except:
                        pass
                if os.path.exists(laugh_file):
                    laugh_clip = AudioFileClip(laugh_file)
                    start_time = max(0, current_time + clip_dur - 1.2)
                    laugh_clip = laugh_clip.with_start(start_time).with_effects([MultiplyVolume(1.8)])
                    combined_audio_clips.append(laugh_clip)
            current_time += clip_dur
            
        if os.path.exists(bgm_path):
            print("Adding background music with fades...")
            bgm = AudioFileClip(bgm_path).with_effects([MultiplyVolume(0.15)])
            if bgm.duration < final_video_clip.duration:
                bgm = bgm.with_effects([AudioLoop(duration=final_video_clip.duration)])
            else:
                bgm = bgm.subclipped(0, final_video_clip.duration)
            
            # Fade in and Fade out for BGM
            bgm = bgm.with_effects([AudioFadeIn(duration=2.0), AudioFadeOut(duration=2.0)])
            combined_audio_clips.append(bgm)
            
        final_video_clip = final_video_clip.with_audio(CompositeAudioClip(combined_audio_clips))

        print(f"Writing final video: {self.output_path}...")
        final_video_clip.write_videofile(self.output_path, fps=24, codec="libx264", audio_codec="aac")
        
        print("Cleaning up temporary files...")
        if os.path.exists("temp_intro.jpg"): os.remove("temp_intro.jpg")
        for i in range(len(scenes)):
            for f in [f"temp_fallback_{i}.jpg", f"temp_voice_{i}.mp3", f"temp_img_text_{i}.jpg", f"temp_laugh_{i}.mp3"]:
                if os.path.exists(f): os.remove(f)
            
        print("Generation Complete! Engine v7 finished.")

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "bragging_dog_v7.mp4"
    engine = JokeVideoEngineV7(script, output)
    engine.generate()
