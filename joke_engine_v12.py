# -*- coding: utf-8 -*-
"""
Joke Video Engine v12 (Dynamic Subtitles & Emotion Edition)
THE TRUE ULTIMATE EDITION - Professional Pro Max Version.
Features:
- Dynamic Word-Level Subtitles (Karaoke Highlight)
- Ken Burns Smooth Zoom & Pan Effects
- Emotional Avatar Reactions (Glow/Shake/Scale)
- Optimized Scene Transitions & SFX
"""

import os
import re
import asyncio
import random
import time
import json
import numpy as np
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip, VideoClip
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.video.fx.Resize import Resize
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut

class JokeVideoEngineV12:
    def __init__(self, script_path, output_path="joke_v12.mp4", is_shorts=False, assets_dir="assets"):
        self.script_path = script_path
        self.output_path = output_path
        self.is_shorts = is_shorts
        self.assets_dir = assets_dir
        self.size = (720, 1280) if is_shorts else (1280, 720)
        
        self.voices = {
            "default": "zh-TW-HsiaoChenNeural",
            "dog": "zh-TW-YunJheNeural",
            "owner": "zh-TW-HsiaoYuNeural"
        }
        
        self.sfx_files = {
            "whoosh": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\whoosh.wav",
            "ding": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\ding.wav"
        }
        
        self.avatar_files = {
            "dog": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\avatar_cute.jpg",
            "owner": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\avatar.jpg",
            "default": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\avatar_cute.jpg"
        }
        
        self.font_path = "C:\\Windows\\Fonts\\msjhbd.ttc"
        if not os.path.exists(self.font_path):
            self.font_path = "C:\\Windows\\Fonts\\simhei.ttf"

        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)

    def _get_circular_avatar(self, character, size=250, emotion="neutral"):
        path = self.avatar_files.get(character, self.avatar_files["default"])
        if not os.path.exists(path):
            img = Image.new('RGBA', (size, size), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, size, size), fill=(0, 255, 255, 255))
        else:
            img = Image.open(path).convert("RGBA")
            img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            output = Image.new('RGBA', (size, size), (0,0,0,0))
            output.paste(img, (0, 0), mask=mask)
            img = output

        # Apply Emotion Effects
        draw_border = ImageDraw.Draw(img)
        border_color = (0, 255, 255, 255) if character == "dog" else (255, 255, 0, 255)
        if emotion == "excited" or emotion == "punchline":
            border_color = (255, 50, 50, 255)
            # Add a glow effect
            img = img.filter(ImageFilter.GaussianBlur(radius=2)) # Subtle glow
            
        draw_border.ellipse((5, 5, size-5, size-5), outline=border_color, width=10)
        return img

    def _add_bouncing_avatar(self, character, duration, is_punchline=False):
        emotion = "punchline" if is_punchline else "neutral"
        avatar_img = self._get_circular_avatar(character, emotion=emotion)
        temp_path = f"temp_avatar_{character}_{time.time()}.png"
        avatar_img.save(temp_path)
        
        base_y = self.size[1] - 450 if not self.is_shorts else self.size[1] - 650
        base_x = 150 if not self.is_shorts else 150
        
        def bounce(t):
            # Normal bounce
            y_offset = -30 * abs(np.sin(2 * np.pi * 1.5 * t))
            if is_punchline:
                # Shake on punchline
                y_offset += random.randint(-5, 5)
            return (base_x, base_y + y_offset)
            
        clip = ImageClip(temp_path).with_duration(duration).with_position(bounce).with_effects([CrossFadeIn(duration=0.3)])
        return clip, temp_path

    def _add_ken_burns(self, img_path, duration):
        # Create a Ken Burns effect (Zoom In)
        base_img = Image.open(img_path).convert("RGB")
        w, h = self.size
        
        # Background: Blurred
        bg_img = base_img.resize(self.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=30))
        bg_draw = ImageDraw.Draw(bg_img, "RGBA")
        bg_draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 120))
        bg_path = f"temp_bg_{time.time()}.jpg"
        bg_img.save(bg_path)
        bg_clip = ImageClip(bg_path).with_duration(duration)
        
        # Foreground: Zoom Effect
        fg_img = Image.open(img_path).convert("RGB")
        img_w, img_h = fg_img.size
        ratio = min(w / img_w, h / img_h) * 0.95
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        fg_img = fg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        fg_path = f"temp_fg_{time.time()}.jpg"
        fg_img.save(fg_path)
        
        fg_clip = ImageClip(fg_path).with_duration(duration).with_position("center")
        
        # Smooth Zoom-in: from 1.0 to 1.15
        fg_clip = fg_clip.with_effects([Resize(lambda t: 1.0 + 0.15 * (t / duration))])
        
        return CompositeVideoClip([bg_clip, fg_clip]), [bg_path, fg_path]

    async def _generate_voice_and_metadata(self, text, audio_file, metadata_file, character="default", rate="+0%", pitch="+0Hz"):
        voice = self.voices.get(character, self.voices["default"])
        clean_text = re.sub(r'[^\w\s，。！？！？,.\u4e00-\u9fa5]', '', text)
        communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
        await communicate.save(audio_file, metadata_file)

    def _add_dynamic_subtitle(self, text, metadata_file, duration, character="default", is_punchline=False):
        w, h = self.size
        bar_h = 350 if self.is_shorts else 220
        
        # Read metadata
        word_timings = []
        if os.path.exists(metadata_file):
            with open(metadata_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data["type"] == "WordBoundary":
                            word_timings.append({
                                "text": data["text"],
                                "start": data["offset"] / 10_000_000,
                                "duration": data["duration"] / 10_000_000
                            })

        try: font_sub = ImageFont.truetype(self.font_path, 75 if self.is_shorts else 85)
        except: font_sub = ImageFont.load_default()
        
        # Pre-wrap the full text to get positions
        dummy_draw = ImageDraw.Draw(Image.new('RGBA', (w, bar_h)))
        full_text = text.strip()
        wrapped_lines, line = [], ""
        for char in full_text:
            line += char
            if dummy_draw.textbbox((0, 0), line, font=font_sub)[2] > w - 120:
                wrapped_lines.append(line); line = ""
        if line: wrapped_lines.append(line)
        
        def render_frame_for_word(current_word_idx):
            img = Image.new('RGBA', (w, bar_h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            # Draw semi-transparent background
            for i in range(bar_h):
                alpha = int(200 * (i / bar_h))
                draw.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))
            
            y = 40
            chars_processed = 0
            for line_text in wrapped_lines:
                line_w = draw.textbbox((0, 0), line_text, font=font_sub)[2]
                x = (w - line_w) / 2
                for char in line_text:
                    char_color = (255, 255, 255, 255)
                    current_pos_in_text = full_text.find(char, chars_processed)
                    is_highlighted = False
                    if current_word_idx != -1:
                        words_str = "".join([wt["text"] for wt in word_timings[:current_word_idx+1]])
                        if current_pos_in_text < len(words_str) and current_pos_in_text >= len("".join([wt["text"] for wt in word_timings[:current_word_idx]])):
                            is_highlighted = True
                    if is_highlighted:
                        char_color = (255, 255, 0, 255)
                        if is_punchline: char_color = (255, 50, 50, 255)
                    elif is_punchline: char_color = (255, 200, 200, 255)
                    elif character == "dog": char_color = (200, 255, 255, 255)
                    draw.text((x+4, y+4), char, font=font_sub, fill=(0,0,0,180))
                    draw.text((x, y), char, font=font_sub, fill=char_color)
                    x += draw.textbbox((0, 0), char, font=font_sub)[2]
                    chars_processed += 1
                y += 100
            return img

        # Create clips for each word segment
        subtitle_clips = []
        last_time = 0
        # 0.25 offset for audio start
        # Initial neutral
        if word_timings and word_timings[0]["start"] > 0:
            img = render_frame_for_word(-1)
            temp_p = f"temp_sub_init_{time.time()}.png"
            img.save(temp_p)
            subtitle_clips.append(ImageClip(temp_p).with_duration(word_timings[0]["start"] + 0.25).with_start(0))
            last_time = word_timings[0]["start"] + 0.25
        elif not word_timings:
            img = render_frame_for_word(-1)
            temp_p = f"temp_sub_none_{time.time()}.png"
            img.save(temp_p)
            return ImageClip(temp_p).with_duration(duration).with_position(("center", h - bar_h - 100))

        for idx, wt in enumerate(word_timings):
            img = render_frame_for_word(idx)
            temp_p = f"temp_sub_{idx}_{time.time()}.png"
            img.save(temp_p)
            start_t = wt["start"] + 0.25
            dur = wt["duration"]
            subtitle_clips.append(ImageClip(temp_p).with_duration(dur).with_start(start_t))
            last_time = start_t + dur

        # Final neutral or trailing
        if last_time < duration:
            img = render_frame_for_word(-1)
            temp_p = f"temp_sub_end_{time.time()}.png"
            img.save(temp_p)
            subtitle_clips.append(ImageClip(temp_p).with_duration(duration - last_time).with_start(last_time))

        return CompositeVideoClip(subtitle_clips).with_position(("center", h - bar_h - 100))

    def _generate_thumbnail(self, scene, i):
        print("🖼️ Generating V12 Cinematic Thumbnail...", flush=True)
        img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
        if not os.path.exists(img_file): return
        
        base = Image.open(img_file).convert("RGB")
        w, h = base.size
        base = base.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=3))
        draw = ImageDraw.Draw(base)
        
        # Clickbait Arrow/Circle
        draw.ellipse([w//2-150, h//2-150, w//2+150, h//2+150], outline=(255, 0, 0), width=25)
        
        try: font_thumb = ImageFont.truetype(self.font_path, 160)
        except: font_thumb = ImageFont.load_default()
        
        title_text = "結局神反轉！😱"
        tw = draw.textbbox((0,0), title_text, font=font_thumb)[2]
        tx, ty = (w - tw) // 2, 80
        for dx, dy in [(-8,-8),(8,8),(-8,8),(8,-8)]:
            draw.text((tx+dx, ty+dy), title_text, font=font_thumb, fill=(0,0,0))
        draw.text((tx, ty), title_text, font=font_thumb, fill=(255, 255, 0))
        
        base.save("thumbnail_v12.png")
        print("✅ Thumbnail saved: thumbnail_v12.png", flush=True)

    def generate(self):
        print(f"🚀 V12 Engine (Pro Pro Max) Started - Shorts: {self.is_shorts}", flush=True)
        scenes, video_title = self._parse_script()
        clips, temp_files, current_time = [], [], 0
        
        # Process all scenes
        for i, scene in enumerate(scenes):
            print(f"🎬 Scene {i+1}: {scene['title']}", flush=True)
            img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            if not os.path.exists(img_file):
                img_file = f"temp_fallback_{i}.jpg"
                img = Image.new('RGB', (1920, 1080), color=(20, 20, 40))
                ImageDraw.Draw(img).text((100, 450), scene['title'], fill=(0, 255, 255))
                img.save(img_file); temp_files.append(img_file)
            
            if scene["is_punchline"]: self._generate_thumbnail(scene, i)
            
            audio_file = f"temp_voice_{i}.mp3"
            metadata_file = f"temp_meta_{i}.json"
            rate, pitch, emoji = self._analyze_emotion_and_emoji(scene["voice"], scene["is_punchline"], scene["character"])
            asyncio.run(self._generate_voice_and_metadata(scene["voice"], audio_file, metadata_file, scene["character"], rate=rate, pitch=pitch))
            
            audio_clip = AudioFileClip(audio_file)
            combined_audio_list = [audio_clip.with_start(0.25)]
            if i > 0 and os.path.exists(self.sfx_files["whoosh"]):
                combined_audio_list.append(AudioFileClip(self.sfx_files["whoosh"]).with_start(0).with_effects([MultiplyVolume(0.4)]))
            if scene["is_punchline"] and os.path.exists(self.sfx_files["ding"]):
                combined_audio_list.append(AudioFileClip(self.sfx_files["ding"]).with_start(audio_clip.duration - 0.2))
                
            audio_scene = CompositeAudioClip(combined_audio_list).with_duration(audio_clip.duration + 0.8)
            temp_files.extend([audio_file, metadata_file])
            
            # 1. Ken Burns Layout
            main_clip, bg_f = self._add_ken_burns(img_file, audio_scene.duration)
            temp_files.extend(bg_f)
            
            # 2. Dynamic Dynamic Subtitles
            sub_clip = self._add_dynamic_subtitle(scene["voice"], metadata_file, audio_scene.duration, scene["character"], scene["is_punchline"])
            
            # 3. Emotional Avatar
            avatar_clip, av_f = self._add_bouncing_avatar(scene["character"], audio_scene.duration, scene["is_punchline"])
            temp_files.append(av_f)
            
            scene_clip = CompositeVideoClip([main_clip, sub_clip, avatar_clip])
            
            if i > 0: scene_clip = scene_clip.with_effects([CrossFadeIn(duration=0.5)])
            scene_clip = scene_clip.with_audio(audio_scene)
            clips.append(scene_clip)
            current_time += scene_clip.duration
            
        final_video = concatenate_videoclips(clips, method="compose")
        
        bgm_path = r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\bgm.wav"
        if os.path.exists(bgm_path):
            bgm = AudioFileClip(bgm_path)
            if bgm.duration < final_video.duration: bgm = bgm.with_effects([AudioLoop(duration=final_video.duration)])
            else: bgm = bgm.subclipped(0, final_video.duration)
            bgm = bgm.with_effects([MultiplyVolume(0.12)])
            final_video = final_video.with_audio(CompositeAudioClip([final_video.audio, bgm]))
            
        print(f"🎬 Writing Final Video: {self.output_path}", flush=True)
        # Lower bitrate and FPS for faster processing in this environment
        final_video.write_videofile(self.output_path, fps=15, codec="libx264", audio_codec="aac", bitrate="1000k")
        print("🧹 Cleaning up...", flush=True)
        for f in temp_files:
            try: os.remove(f)
            except: pass
        print("✅ V12 Professional Edition Complete!", flush=True)

    def _analyze_emotion_and_emoji(self, text, is_punchline, character):
        rate, pitch, emoji = "+0%", "+0Hz", ""
        if is_punchline: rate, pitch, emoji = "+15%", "+10Hz", "🔥"
        elif "！" in text: rate, pitch, emoji = "+5%", "+3Hz", "❗"
        if not emoji: emoji = "🐶" if character == "dog" else "👱‍♂️"
        return rate, pitch, emoji

    def _parse_script(self):
        with open(self.script_path, 'r', encoding='utf-8') as f: content = f.read()
        scenes = []
        video_title = "笑話時間"
        parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
        for i, part in enumerate(parts):
            if not part.strip(): continue
            lines = part.strip().split('\n')
            title = lines[0].strip()
            voice_text, character = [], "default"
            for line in lines[1:]:
                line = line.strip()
                if '旁白' in line and '**' in line: voice_text.append(re.sub(r'- \*\*.*?\*\*：?', '', line).strip())
                elif '狗狗' in line and '**' in line: voice_text.append(re.sub(r'- \*\*.*?\*\*：?', '', line).strip()); character = "dog"
                elif '屋主' in line and '**' in line: voice_text.append(re.sub(r'- \*\*.*?\*\*：?', '', line).strip()); character = "owner"
            combined_voice = " ".join(voice_text).strip()
            if combined_voice:
                scenes.append({"title": title, "voice": combined_voice, "character": character, "is_punchline": any(k in title for k in ["結尾", "反轉", "高潮"])})
        return scenes, video_title

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "joke_v12.mp4"
    assets = sys.argv[3] if len(sys.argv) > 3 else "assets"
    engine = JokeVideoEngineV12(script, output, is_shorts=True, assets_dir=assets)
    engine.generate()
