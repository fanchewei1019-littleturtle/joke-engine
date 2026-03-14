# Joke Video Engine 🐢🎥✨

The Joke Video Engine is an automated tool for generating high-quality joke videos with AI-generated images, voices, and dynamic subtitles. It's designed to create engaging content for platforms like YouTube Shorts and TikTok.

## Features

- **Automated Script Parsing**: Automatically extracts scenes, dialogues, and image prompts from Markdown scripts.
- **AI Image Generation**: Integrated with SiliconFlow Flux.1-schnell API for cinematic, high-quality images.
- **Edge TTS Integration**: Generates natural-sounding voices for different characters.
- **Dynamic Subtitles**: Word-level highlighted subtitles synced with the voice.
- **Visual Transitions**: Ken Burns effect (zoom), cross-fades, and bouncing avatars for dynamic visual storytelling.
- **Asset Management**: Supports fallback logic for missing assets and organizes media efficiently.
- **Customizable**: Supports different video formats (Landscape/Shorts) and asset directories.

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

3.  **Set up API Key**:
    Set your SiliconFlow API key as an environment variable:
    ```bash
    export SILICONFLOW_API_KEY="your_api_key_here"
    ```

## Usage

Create a script in Markdown format (see `script.md` for example) and run the engine:

```bash
python joke_engine_v14.py script.md output_video.mp4 assets_dir
```

- `script.md`: Path to your joke script.
- `output_video.mp4`: Desired output filename.
- `assets_dir`: Directory to store generated images for the video.

## Directory Structure

- `assets/`: Contains core audio (BGM, SFX) and avatar images.
- `joke_engine_v14.py`: The latest version of the video generation engine.
- `.gitignore`: Configured to exclude temporary files and large media.

## License

This project is for educational and personal use. Created by **aicay**.
