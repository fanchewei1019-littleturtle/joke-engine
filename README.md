# Joke Video Engine 🐢🎥✨

The Joke Video Engine is an automated tool for generating high-quality joke videos with AI-generated images, voices, and dynamic subtitles. It's designed to create engaging content for platforms like YouTube Shorts and TikTok.

## Features

- **Automated Script Parsing**: Automatically extracts scenes, dialogues, and image prompts from Markdown scripts.
- **AI Image Generation**: Multi-tier generation logic:
    1. **SiliconFlow Flux.1-schnell**: High-quality cinematic images.
    2. **Pollinations.ai**: Reliable secondary fallback.
    3. **LoremFlickr**: Absolute fallback ensures the process never fails.
- **Edge TTS Integration**: Generates natural-sounding voices for different characters, with default 1.5x speed support.
- **Dynamic Subtitles**: Word-level highlighted subtitles synced with the voice.
- **Visual Transitions**: Ken Burns effect (zoom), cross-fades, and bouncing avatars for dynamic visual storytelling.
- **Turtle Special Edition**: Built-in support for "小烏龜" (Little Turtle) character, including custom avatars and voices.
- **Asset Management**: Organizes media efficiently and supports fallback assets.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/aicay/joke-engine.git
    cd joke-engine
    ```

2.  **Install dependencies**:
    ```bash
    pip install moviepy pillow requests numpy edge-tts
    ```

3.  **Set up API Key (Optional but recommended)**:
    Set your SiliconFlow API key as an environment variable:
    ```bash
    export SILICONFLOW_API_KEY="your_api_key_here"
    ```

## Usage

Create a script in Markdown format (see `night_thoughts_script.md` for example) and run the latest engine:

```bash
python v15_turtle_engine.py script.md output_video.mp4 assets_dir
```

- `script.md`: Path to your script.
- `output_video.mp4`: Desired output filename.
- `assets_dir`: Directory to store generated images for the video.

## Directory Structure

- `assets/`: Contains core audio (BGM, SFX) and avatar images.
- `v15_turtle_engine.py`: The latest version of the video generation engine (Turtle Edition).
- `joke_engine_v14.py`: The standard SiliconFlow edition.
- `.gitignore`: Configured to exclude temporary files and large media.

## License

This project is for educational and personal use. Created by **aicay**.
