# -*- coding: utf-8 -*-
"""
Joke Video Engine v15 (Little Turtle Special Edition) 🐢🎥✨
Changes:
- Support for "小烏龜" character and voices.
- Integrated Pollinations.ai as a secondary image generation fallback.
- Default speech rate set to +50% (1.5x) as requested.
- Enhanced layout for turtle-themed content.
"""

import os
import re
import asyncio
import random
import time
import json
import requests
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

# SiliconFlow API Key - Priority: Environment Variable > Placeholder
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx") 

class TurtleVideoEngineV15:
    def __init__(self, script_path, output_path="turtle_thoughts.mp4", is_shorts=True, assets_dir="assets_turtle"):
        self.script_path = script_path
        self.output_path = output_path
        self.is_shorts = is_shorts
        self.assets_dir = assets_dir
        self.size = (720, 1280) if is_shorts else (1280, 720)
        
        self.voices = {
            "default": "zh-TW-HsiaoChenNeural",
            "旁白": "zh-TW-HsiaoChenNeural",
            "小烏龜": "zh-TW-YunJheNeural", # Slightly younger/cute male voice
        }
        
        self.sfx_files = {
            "whoosh": os.path.join("assets", "audio", "whoosh.wav"),
            "ding": os.path.join("assets", "audio", "ding.wav")
        }
        
        # We will generate the turtle avatar if it doesn't exist
        self.avatar_files = {
            "小烏龜": os.path.join(self.assets_dir, "turtle_avatar.png"),
            "default": os.path.join(self.assets_dir, "turtle_avatar.png")
        }
        
        self.font_path = "C:\\Windows\\Fonts\\msjhbd.ttc"
        if not os.path.exists(self.font_path):
            self.font_path = "C:\\Windows\\Fonts\\simhei.ttf"

        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)

    def _get_circular_avatar(self, character, size=250):
        path = self.avatar_files.get(character, self.avatar_files["default"])
        if not os.path.exists(path):
            # Generate a turtle avatar using pollinations if not exists
            print(f"Generating turtle avatar at {path}...")
            prompt = "A very cute 3D turtle avatar, glowing green shell, soft blue eyes, Pixar style, high quality, close up."
            url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512&seed={random.randint(1, 10000)}&nologo=true"
            success = False
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200 and b"error" not in response.content[:100]:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    success = True
            except: pass
            
            if not success:
                # Absolute fallback: Green circle
                print("Using green circle fallback for avatar.")
                img = Image.new('RGBA', (size, size), (0,0,0,0))
                draw = ImageDraw.Draw(img)
                draw.ellipse((0, 0, size, size), fill=(0, 255, 0, 255))
                img.save(path)

        img = Image.open(path).convert("RGBA")
        img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        blurred_mask = mask.filter(ImageFilter.GaussianBlur(radius=1.5)) 
        output = Image.new('RGBA', (size, size), (0,0,0,0))
        output.paste(img, (0, 0), mask=blurred_mask)
        
        draw_border = ImageDraw.Draw(output)
        border_color = (0, 255, 0, 255) # Green for turtle
        draw_border.ellipse((5, 5, size-5, size-5), outline=border_color, width=10)
        return output

    def _add_bouncing_avatar(self, character, start_t, duration):
        if character == "旁白" or character == "default":
            return None, None
        avatar_img = self._get_circular_avatar(character)
        temp_path = f"temp_avatar_{character}_{time.time()}.png"
        avatar_img.save(temp_path)
        
        # Position at the bottom left for Little Turtle
        base_y = self.size[1] - 450 if not self.is_shorts else self.size[1] - 650
        base_x = 80 if self.is_shorts else 150
        
        def bounce(t):
            y_offset = -20 * abs(np.sin(2 * np.pi * 2.0 * t))
            return (base_x, base_y + y_offset)
            
        clip = ImageClip(temp_path).with_duration(duration).with_start(start_t).with_position(bounce).with_effects([CrossFadeIn(duration=0.2)])
        return clip, temp_path

    def _add_ken_burns(self, img_path, duration, zoom_magnitude=0.15):
        base_img = Image.open(img_path).convert("RGB")
        w, h = self.size
        # Background: Blurred version of the image
        bg_img = base_img.resize(self.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=30))
        bg_draw = ImageDraw.Draw(bg_img, "RGBA")
        bg_draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 150)) # Darker for philosophy theme
        bg_path = f"temp_bg_{time.time()}.jpg"
        bg_img.save(bg_path)
        bg_clip = ImageClip(bg_path).with_duration(duration)
        
        # Foreground: Zooming image
        fg_img = Image.open(img_path).convert("RGB")
        img_w, img_h = fg_img.size
        initial_ratio = min(w / img_w, h / img_h) * 0.95
        initial_w, initial_h = int(img_w * initial_ratio), int(img_h * initial_ratio)
        fg_img = fg_img.resize((initial_w, initial_h), Image.Resampling.LANCZOS)
        fg_path = f"temp_fg_{time.time()}.jpg"
        fg_img.save(fg_path)
        fg_clip = ImageClip(fg_path).with_duration(duration).with_position("center")
        
        def ease_in_out_cubic(t_ratio): return t_ratio * t_ratio * (3.0 - 2.0 * t_ratio)
        def zoom_scale(t):
            t_ratio = t / duration
            return 1.0 + zoom_magnitude * ease_in_out_cubic(t_ratio)
        
        fg_clip = fg_clip.with_effects([Resize(zoom_scale)])
        final_clip = CompositeVideoClip([bg_clip, fg_clip.with_position(("center", "center"))])
        return final_clip, [bg_path, fg_path]

    async def _generate_voice_and_metadata(self, text, audio_file, metadata_file, character="default", rate="+50%", pitch="+0Hz"):
        voice = self.voices.get(character, self.voices["default"])
        # Remove emojis for compatibility as requested
        clean_text = re.sub(r'[^\w\s，。！？！？,.\u4e00-\u9fa5]', '', text)
        communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
        await communicate.save(audio_file, metadata_file)

    def _add_dynamic_subtitle(self, text, metadata_file, start_offset, segment_duration, character="default"):
        w, h = self.size
        bar_h = 350 if self.is_shorts else 220
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
            # Gradient shadow for readability
            for i in range(bar_h):
                alpha = int(220 * (i / bar_h))
                draw.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))
            y, chars_processed = 40, 0
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
                        char_color = (0, 255, 0, 255) # Green highlight for turtle theme
                    elif character == "小烏龜": char_color = (200, 255, 200, 255)
                    draw.text((x+4, y+4), char, font=font_sub, fill=(0,0,0,200)) # Stronger shadow
                    draw.text((x, y), char, font=font_sub, fill=char_color)
                    x += draw.textbbox((0, 0), char, font=font_sub)[2]
                    chars_processed += 1
                y += 100
            return img

        subtitle_clips, temp_ps = [], []
        audio_offset = 0.15 # Reduced offset for faster speech
        if not word_timings:
            img = render_frame_for_word(-1)
            temp_p = f"temp_sub_none_{time.time()}.png"
            img.save(temp_p)
            return [ImageClip(temp_p).with_duration(segment_duration).with_start(start_offset).with_position(("center", h - bar_h - 100))], [temp_p]

        for idx, wt in enumerate(word_timings):
            img = render_frame_for_word(idx)
            temp_p = f"temp_sub_{idx}_{time.time()}.png"
            img.save(temp_p); temp_ps.append(temp_p)
            s_t = start_offset + wt["start"] + audio_offset
            subtitle_clips.append(ImageClip(temp_p).with_duration(wt["duration"]).with_start(s_t))
            last_time = wt["start"] + wt["duration"] + audio_offset

        img = render_frame_for_word(-1)
        tp_init = f"temp_sub_init_{time.time()}.png"
        img.save(tp_init); temp_ps.append(tp_init)
        subtitle_clips.insert(0, ImageClip(tp_init).with_duration(word_timings[0]["start"] + audio_offset).with_start(start_offset))
        if last_time < segment_duration:
            tp_end = f"temp_sub_end_{time.time()}.png"
            img.save(tp_end); temp_ps.append(tp_end)
            subtitle_clips.append(ImageClip(tp_end).with_duration(segment_duration - last_time).with_start(start_offset + last_time))
        return subtitle_clips, temp_ps

    def _generate_images(self, scenes):
        print("--- Image Generation Started ---")
        
        for i, scene in enumerate(scenes):
            filename = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            if os.path.exists(filename):
                print(f"Scene {i+1} image already exists. Skipping.")
                continue
            
            prompt = scene.get("image_prompt", scene["title"])
            print(f"Generating image for Scene {i+1}: {prompt}")
            
            success = False
            # Try SiliconFlow first
            if SILICONFLOW_API_KEY != "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
                url = "https://api.siliconflow.cn/v1/images/generations"
                headers = {"Authorization": f"Bearer {SILICONFLOW_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "black-forest-labs/FLUX.1-schnell",
                    "prompt": f"{prompt}, high quality, cinematic, 3D render, Pixar style",
                    "image_size": "1024x576" if not self.is_shorts else "576x1024"
                }
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=60)
                    if response.status_code == 200:
                        image_url = response.json()["images"][0]["url"]
                        img_data = requests.get(image_url).content
                        with open(filename, 'wb') as f: f.write(img_data)
                        print(f"Successfully generated via SiliconFlow: {filename}")
                        success = True
                except: pass
            
            # Try Pollinations as fallback
            if not success:
                print(f"Using Pollinations fallback for Scene {i+1}...")
                w, h = (720, 1280) if self.is_shorts else (1280, 720)
                safe_prompt = requests.utils.quote(prompt + ", high quality, cinematic, 3D render, Pixar style, cute turtle")
                poll_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={w}&height={h}&seed={random.randint(1, 10000)}&nologo=true"
                try:
                    response = requests.get(poll_url, timeout=45)
                    if response.status_code == 200 and b"error" not in response.content[:100]:
                        with open(filename, 'wb') as f: f.write(response.content)
                        print(f"Successfully generated via Pollinations: {filename}")
                        success = True
                    else:
                        print(f"Pollinations failed (status {response.status_code} or error in content).")
                except: pass
            
            # Absolute fallback: LoremFlickr
            if not success:
                print(f"Using LoremFlickr absolute fallback for Scene {i+1}...")
                w, h = (720, 1280) if self.is_shorts else (1280, 720)
                flickr_url = f"https://loremflickr.com/{w}/{h}/turtle,sea,digital?lock={random.randint(1, 1000)}"
                try:
                    response = requests.get(flickr_url, timeout=30)
                    if response.status_code == 200:
                        with open(filename, 'wb') as f: f.write(response.content)
                        print(f"Successfully fetched via LoremFlickr: {filename}")
                        success = True
                except: pass

    def generate(self):
        print(f" Turtle Engine v15 Started - Shorts: {self.is_shorts}", flush=True)
        scenes, video_title = self._parse_script()
        
        # Ensure avatar exists
        self._get_circular_avatar("小烏龜")
        
        # Step 1: Generate Images
        self._generate_images(scenes)
        
        clips, temp_files = [], []
        for i, scene in enumerate(scenes):
            print(f" Processing Scene {i+1}: {scene['title']}", flush=True)
            img_file = os.path.join(self.assets_dir, f"scene_{i+1}.jpg")
            if not os.path.exists(img_file):
                img_file = f"temp_fallback_{i}.jpg"
                img = Image.new('RGB', (1920, 1080), color=(10, 10, 30))
                ImageDraw.Draw(img).text((100, 450), scene['title'], fill=(0, 255, 0))
                img.save(img_file); temp_files.append(img_file)
            
            scene_audio_list, scene_sub_clips, scene_avatar_clips, scene_time = [], [], [], 0
            if i > 0 and os.path.exists(self.sfx_files["whoosh"]):
                scene_audio_list.append(AudioFileClip(self.sfx_files["whoosh"]).with_start(0).with_effects([MultiplyVolume(0.3)]))

            for d_idx, dial in enumerate(scene["dialogues"]):
                char, text = dial["character"], dial["text"]
                audio_f, meta_f = f"temp_v_{i}_{d_idx}.mp3", f"temp_m_{i}_{d_idx}.json"
                asyncio.run(self._generate_voice_and_metadata(text, audio_f, meta_f, char))
                
                audio_clip = AudioFileClip(audio_f)
                segment_dur = audio_clip.duration + 0.3 # Slightly tighter
                scene_audio_list.append(audio_clip.with_start(scene_time + 0.15))
                
                sub_seg_clips, sub_temps = self._add_dynamic_subtitle(text, meta_f, scene_time, segment_dur, char)
                scene_sub_clips.extend(sub_seg_clips); temp_files.extend(sub_temps)
                
                av_clip, av_f = self._add_bouncing_avatar(char, scene_time, segment_dur)
                if av_clip: scene_avatar_clips.append(av_clip); temp_files.append(av_f)
                
                scene_time += segment_dur
                temp_files.extend([audio_f, meta_f])

            audio_scene = CompositeAudioClip(scene_audio_list).with_duration(scene_time)
            main_clip, bg_f = self._add_ken_burns(img_file, scene_time)
            temp_files.extend(bg_f)
            sub_overlay = CompositeVideoClip(scene_sub_clips).with_position(("center", self.size[1] - (350 if self.is_shorts else 220) - 100))
            scene_clip = CompositeVideoClip([main_clip, sub_overlay] + scene_avatar_clips).with_duration(scene_time)
            if i > 0: scene_clip = scene_clip.with_effects([CrossFadeIn(duration=0.4)])
            scene_clip = scene_clip.with_audio(audio_scene)
            clips.append(scene_clip)
            
        final_video = concatenate_videoclips(clips, method="compose")
        bgm_path = os.path.join("assets", "audio", "bgm_chill.wav")
        if not os.path.exists(bgm_path): bgm_path = os.path.join("assets", "audio", "bgm.wav")
        
        if os.path.exists(bgm_path):
            bgm = AudioFileClip(bgm_path)
            if bgm.duration < final_video.duration: bgm = bgm.with_effects([AudioLoop(duration=final_video.duration)])
            else: bgm = bgm.subclipped(0, final_video.duration)
            bgm = bgm.with_effects([MultiplyVolume(0.1)])
            final_video = final_video.with_audio(CompositeAudioClip([final_video.audio, bgm]))
            
        final_video.write_videofile(self.output_path, fps=24, codec="libx264", audio_codec="aac", bitrate="2000k")
        for f in temp_files:
            try: os.remove(f)
            except: pass
        print(" Turtle Engine v15 Complete!", flush=True)

    def _parse_script(self):
        with open(self.script_path, 'r', encoding='utf-8') as f: content = f.read()
        scenes = []
        parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
        for i, part in enumerate(parts):
            if not part.strip(): continue
            lines = part.strip().split('\n')
            title = lines[0].strip()
            dialogues = []
            image_prompt = ""
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("- **Image Prompt**"):
                    image_prompt = line.split(":", 1)[1].strip()
                    continue
                match = re.match(r'- \*\*(.*?)\*\*：?(.*)', line)
                if match:
                    char_label, text = match.groups()
                    clean_char = "小烏龜" if "小烏龜" in char_label else "旁白"
                    clean_text = re.sub(r'\(.*?\)', '', text).strip()
                    if clean_text: dialogues.append({"character": clean_char, "text": clean_text})
            if dialogues:
                scenes.append({
                    "title": title, 
                    "dialogues": dialogues, 
                    "image_prompt": image_prompt
                })
        return scenes, "小烏龜的夜後思考"

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "night_thoughts_script.md"
    output = sys.argv[2] if len(sys.argv) > 2 else "turtle_thoughts_v15.mp4"
    assets = sys.argv[3] if len(sys.argv) > 3 else "assets_turtle"
    engine = TurtleVideoEngineV15(script, output, is_shorts=True, assets_dir=assets)
    engine.generate()
