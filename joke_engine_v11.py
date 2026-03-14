# -*- coding: utf-8 -*-
"""
Joke Video Engine v11 (Cinematic SFX & Thumbnail Edition)
THE TRUE ULTIMATE EDITION - Milestone Version.
Features:
- EVERYTHING from V10
- Automated Transition SFX (Whoosh)
- Punchline SFX (Ding/Bell)
- Automatic High-Impact Thumbnail Generation (thumbnail.png)
- Enhanced Intro/Outro screens
"""

import os
import re
import asyncio
import random
import time
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

class JokeVideoEngineV11:
    def __init__(self, script_path, output_path="joke_v11.mp4", is_shorts=False, assets_dir="assets"):
        self.script_path = script_path
        self.output_path = output_path
        self.is_shorts = is_shorts
        self.assets_dir = assets_dir
        self.size = (1080, 1920) if is_shorts else (1920, 1080)
        
        self.voices = {
            "default": "zh-TW-HsiaoChenNeural",
            "dog": "zh-TW-YunJheNeural",
            "owner": "zh-TW-HsiaoYuNeural"
        }
        
        # SFX mapping
        self.sfx_files = {
            "whoosh": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\whoosh.wav",
            "ding": r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\ding.wav"
        }
        
        # Avatar files
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

    def _get_circular_avatar(self, character, size=250):
        path = self.avatar_files.get(character, self.avatar_files["default"])
        if not os.path.exists(path):
            img = Image.new('RGBA', (size, size), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, size, size), fill=(0, 255, 255, 255))
            return img
        img = Image.open(path).convert("RGBA")
        img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        output = Image.new('RGBA', (size, size), (0,0,0,0))
        output.paste(img, (0, 0), mask=mask)
        draw_border = ImageDraw.Draw(output)
        border_color = (0, 255, 255, 255) if character == "dog" else (255, 255, 0, 255)
        draw_border.ellipse((5, 5, size-5, size-5), outline=border_color, width=8)
        return output

    def _add_bouncing_avatar(self, character, duration):
        avatar_img = self._get_circular_avatar(character)
        temp_path = f"temp_avatar_{character}_{time.time()}.png"
        avatar_img.save(temp_path)
        base_y = self.size[1] - 450 if not self.is_shorts else self.size[1] - 650
        base_x = 150 if not self.is_shorts else 150
        def bounce(t):
            y_offset = -30 * abs(np.sin(2 * np.pi * 1.5 * t))
            return (base_x, base_y + y_offset)
        clip = ImageClip(temp_path).with_duration(duration).with_position(bounce).with_effects([CrossFadeIn(duration=0.3)])
        return clip, temp_path

    def _add_particle_overlay(self, duration):
        w, h = self.size
        n_particles = 25
        particles = [{"x": random.randint(0, w), "y": random.randint(0, h), "v": random.uniform(20, 50), "s": random.randint(2, 5)} for _ in range(n_particles)]
        def make_frame(t):
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            for p in particles:
                curr_y = int((p["y"] - p["v"] * t) % h)
                y, x, s = curr_y, p["x"], p["s"]
                frame[max(0, y-s):min(h, y+s), max(0, x-s):min(w, x+s)] = [255, 255, 255]
            return frame
        return VideoClip(make_frame, duration=duration).with_opacity(0.2)

    def _apply_color_grade(self, clip):
        overlay = ColorClip(self.size, color=(0, 20, 40)).with_duration(clip.duration).with_opacity(0.15)
        return CompositeVideoClip([clip, overlay])

    def _create_smart_layout(self, img_path, duration):
        base_img = Image.open(img_path).convert("RGB")
        bg_img = base_img.resize(self.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=30))
        bg_draw = ImageDraw.Draw(bg_img, "RGBA")
        bg_draw.rectangle([0, 0, self.size[0], self.size[1]], fill=(0, 0, 0, 100))
        bg_path = f"temp_bg_{time.time()}.jpg"
        bg_img.save(bg_path)
        bg_clip = ImageClip(bg_path).with_duration(duration)
        fg_img = Image.open(img_path).convert("RGB")
        target_w, target_h = self.size
        img_w, img_h = fg_img.size
        ratio = min(target_w / img_w, target_h / img_h) * 0.9
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        fg_img = fg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        fg_path = f"temp_fg_{time.time()}.jpg"
        fg_img.save(fg_path)
        fg_clip = ImageClip(fg_path).with_duration(duration).with_position("center")
        return CompositeVideoClip([bg_clip, fg_clip]), [bg_path, fg_path]

    async def _generate_voice(self, text, filename, character="default", rate="+0%", pitch="+0Hz"):
        voice = self.voices.get(character, self.voices["default"])
        clean_text = re.sub(r'[^\w\s，。！？！？,.\u4e00-\u9fa5]', '', text)
        communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch)
        await communicate.save(filename)

    def _analyze_emotion_and_emoji(self, text, is_punchline, character):
        rate, pitch, emoji = "+0%", "+0Hz", ""
        if is_punchline: rate, pitch, emoji = "+20%", "+15Hz", random.choice(["💥", "😂", "🤣", "✨", "🔥"])
        elif "！" in text: rate, pitch, emoji = "+8%", "+5Hz", "❗"
        elif "？" in text: pitch, emoji = "+10Hz", "❓"
        elif "..." in text: rate, pitch, emoji = "-15%", "-8Hz", "💦"
        if not emoji: emoji = "🐶" if character == "dog" else ("👱‍♂️" if character == "owner" else "💬")
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
            if i == 1: video_title = title.replace("結尾", "").replace("反轉", "").strip()
            voice_text, image_desc, character = [], "", "default"
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('- **畫面**'): image_desc = line.replace('- **畫面**：', '').strip()
                elif '旁白' in line and '**' in line: voice_text.append(re.sub(r'- \*\*.*?\*\*：?', '', line).strip())
                elif '狗狗' in line and '**' in line: voice_text.append(re.sub(r'- \*\*.*?\*\*：?', '', line).strip()); character = "dog"
                elif '屋主' in line and '**' in line: voice_text.append(re.sub(r'- \*\*.*?\*\*：?', '', line).strip()); character = "owner"
            combined_voice = " ".join(voice_text).strip()
            if combined_voice or image_desc:
                scenes.append({"title": title, "voice": combined_voice, "image_desc": image_desc, "character": character, "is_punchline": any(k in title for k in ["結尾", "反轉", "高潮"])})
        return scenes, video_title

    def _add_subtitle_to_image(self, base_img_clip, text, emoji="", character="default", is_punchline=False):
        duration = base_img_clip.duration
        w, h = self.size
        bar_h = 300 if self.is_shorts else 200
        txt_img = Image.new('RGBA', (w, bar_h), (0,0,0,0))
        draw = ImageDraw.Draw(txt_img)
        try: font_sub = ImageFont.truetype(self.font_path, 70 if self.is_shorts else 80)
        except: font_sub = ImageFont.load_default()
        full_text = f"{text} {emoji}".strip()
        wrapped_lines, line = [], ""
        for char in full_text:
            line += char
            if draw.textbbox((0, 0), line, font=font_sub)[2] > w - 100:
                wrapped_lines.append(line); line = ""
        if line: wrapped_lines.append(line)
        for i in range(bar_h):
            alpha = int(200 * (i / bar_h))
            draw.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))
        y = 30
        fill_color = (255, 50, 50, 255) if is_punchline else ((100, 200, 255, 255) if character == "dog" else (255, 255, 255, 255))
        for line in wrapped_lines:
            x = (w - draw.textbbox((0, 0), line, font=font_sub)[2]) / 2
            draw.text((x+4, y+4), line, font=font_sub, fill=(0,0,0,200))
            draw.text((x, y), line, font=font_sub, fill=fill_color)
            y += 90
        temp_txt_path = f"temp_sub_{time.time()}.png"
        txt_img.save(temp_txt_path)
        sub_clip = ImageClip(temp_txt_path).with_duration(duration).with_position(("center", h - bar_h - 100))
        return sub_clip, temp_txt_path

    def _generate_thumbnail(self, scene, i):
        print("Generating Cinematic Thumbnail...", flush=True)
        img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
        if not os.path.exists(img_file): return
        
        base = Image.open(img_file).convert("RGB")
        w, h = base.size
        # Make a high-contrast thumbnail
        base = base.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        draw = ImageDraw.Draw(base)
        
        # Add a thick red circle for "clickbait" effect
        draw.ellipse([w//2-100, h//2-100, w//2+100, h//2+100], outline=(255, 0, 0), width=20)
        
        # Add big yellow text with black border
        try: font_thumb = ImageFont.truetype(self.font_path, 150)
        except: font_thumb = ImageFont.load_default()
        
        title_text = "神轉折！主人氣瘋了 😂"
        tw = draw.textbbox((0,0), title_text, font=font_thumb)[2]
        tx, ty = (w - tw) // 2, 50
        # Thick shadow
        for dx, dy in [(-5,-5),(5,5),(-5,5),(5,-5)]:
            draw.text((tx+dx, ty+dy), title_text, font=font_thumb, fill=(0,0,0))
        draw.text((tx, ty), title_text, font=font_thumb, fill=(255, 255, 0))
        
        base.save("thumbnail.png")
        print("Thumbnail saved: thumbnail.png", flush=True)

    def generate(self):
        print(f"V11 Engine (Cinematic Edition) Started - Shorts: {self.is_shorts}", flush=True)
        scenes, video_title = self._parse_script()
        clips, temp_files, voice_segments, current_time = [], [], [], 0
        
        for i, scene in enumerate(scenes):
            print(f"Scene {i+1}: {scene['title']}", flush=True)
            img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            if not os.path.exists(img_file):
                print(f"Warning: {img_file} not found, using fallback.", flush=True)
                img_file = f"temp_fallback_{i}.jpg"
                img = Image.new('RGB', (1920, 1080), color=(20, 20, 40))
                ImageDraw.Draw(img).text((100, 450), scene['title'], fill=(0, 255, 255))
                img.save(img_file); temp_files.append(img_file)
            
            # Thumbnail on punchline
            if scene["is_punchline"]: self._generate_thumbnail(scene, i)
            
            audio_file = f"temp_voice_{i}.mp3"
            if scene["voice"]:
                rate, pitch, emoji = self._analyze_emotion_and_emoji(scene["voice"], scene["is_punchline"], scene["character"])
                asyncio.run(self._generate_voice(scene["voice"], audio_file, scene["character"], rate=rate, pitch=pitch))
                audio_clip = AudioFileClip(audio_file)
            else:
                from moviepy import AudioArrayClip
                audio_clip = AudioArrayClip(np.zeros((44100 * 2, 2)), fps=44100); emoji = ""
            
            # Combine Voice with SFX
            combined_audio_list = [audio_clip.with_start(0.25)]
            
            # SFX 1: Transition Whoosh
            if i > 0 and os.path.exists(self.sfx_files["whoosh"]):
                whoosh = AudioFileClip(self.sfx_files["whoosh"]).with_start(0).with_effects([MultiplyVolume(0.5)])
                combined_audio_list.append(whoosh)
                
            # SFX 2: Punchline Ding
            if scene["is_punchline"] and os.path.exists(self.sfx_files["ding"]):
                ding = AudioFileClip(self.sfx_files["ding"]).with_start(audio_clip.duration - 0.2)
                combined_audio_list.append(ding)
                
            audio_scene = CompositeAudioClip(combined_audio_list).with_duration(audio_clip.duration + 0.8)
            voice_segments.append((current_time + 0.25, current_time + audio_clip.duration - 0.45))
            temp_files.append(audio_file)
            
            main_clip, bg_f = self._create_smart_layout(img_file, audio_scene.duration)
            temp_files.extend(bg_f)
            sub_clip, sub_f = self._add_subtitle_to_image(main_clip, scene["voice"], emoji, scene["character"], scene["is_punchline"])
            temp_files.append(sub_f)
            avatar_clip, av_f = self._add_bouncing_avatar(scene["character"], audio_scene.duration)
            temp_files.append(av_f)
            # particles = self._add_particle_overlay(audio_scene.duration)
            
            scene_clip = CompositeVideoClip([main_clip, sub_clip, avatar_clip]) # Removed particles
            if scene["is_punchline"]:
                scene_clip = scene_clip.with_effects([Resize(lambda t: 1.0 + 0.3 * (t / audio_scene.duration))])
                flash = ColorClip(self.size, color=(255,255,255)).with_duration(0.2).with_effects([CrossFadeOut(duration=0.2)])
                scene_clip = CompositeVideoClip([scene_clip, flash])
            
            if i > 0: scene_clip = scene_clip.with_effects([CrossFadeIn(duration=0.4)])
            scene_clip = scene_clip.with_audio(audio_scene)
            clips.append(scene_clip)
            current_time += scene_clip.duration
            
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = self._apply_color_grade(final_video)
        
        bgm_path = r"C:\Users\chewei\Desktop\littleturtle\joke_factory\assets\bgm.wav"
        if os.path.exists(bgm_path):
            bgm = AudioFileClip(bgm_path)
            if bgm.duration < final_video.duration: bgm = bgm.with_effects([AudioLoop(duration=final_video.duration)])
            else: bgm = bgm.subclipped(0, final_video.duration)
            
            # Manual audio ducking to avoid MultiplyVolume function factor issue
            original_bgm_get_frame = bgm.get_frame
            def duck_factor(t):
                if isinstance(t, np.ndarray):
                    factors = np.ones(t.shape) * 0.12
                    for s, e in voice_segments:
                        mask = (t >= s) & (t <= e)
                        factors[mask] = 0.04
                    return factors[:, np.newaxis]
                return 0.04 if any(s <= t <= e for s,e in voice_segments) else 0.12
            
            bgm = bgm.with_updated_frame_function(lambda t: duck_factor(t) * original_bgm_get_frame(t))
            final_video = final_video.with_audio(CompositeAudioClip([final_video.audio, bgm]))
            
        print(f"Writing Final Video: {self.output_path}", flush=True)
        final_video.write_videofile(self.output_path, fps=24, codec="libx264", audio_codec="aac")
        print("Cleaning up...", flush=True)
        for f in temp_files:
            try: os.remove(f)
            except: pass
        print("V11 Cinematic Turtle Edition Complete!", flush=True)

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "joke_v11.mp4"
    assets = sys.argv[3] if len(sys.argv) > 3 else "assets"
    engine = JokeVideoEngineV11(script, output, is_shorts=True, assets_dir=assets)
    engine.generate()
