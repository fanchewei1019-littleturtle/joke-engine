print("Importing os, re, asyncio, random, time, numpy...", flush=True)
import os
import re
import asyncio
import random
import time
import numpy as np
print("Importing edge_tts...", flush=True)
import edge_tts
print("Importing PIL...", flush=True)
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
print("Importing moviepy basic...", flush=True)
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip, CompositeVideoClip, ColorClip, VideoClip
print("Importing moviepy effects...", flush=True)
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.video.fx.Resize import Resize
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
print("All imports OK.", flush=True)
