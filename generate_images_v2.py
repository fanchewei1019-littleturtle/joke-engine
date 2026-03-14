import os
import re
import requests
import time
import random
from urllib.parse import quote

def parse_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match Image Prompt lines
    prompts = re.findall(r'- \*\*Image Prompt\*\*: (.+)', content)
    return prompts

def download_image(prompt, filename):
    # Using the standard URL format
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(1, 1000000)
    
    # Add quality descriptors to the prompt
    enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting"
    encoded_prompt = quote(enhanced_prompt)
    
    url = f"{base_url}{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true"
    
    print(f"Downloading: {filename}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Short timeout to avoid hanging, Pollinations is fast
            response = requests.get(url, headers=headers, timeout=45) 
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('Content-Type', '')
                if content_type.startswith('image'):
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Successfully saved to {filename} ({content_type})")
                    return True
                else:
                    print(f"Response not an image: {content_type}")
                    # If it's a redirect or something, maybe wait?
            elif response.status_code == 429:
                wait_time = 15 * (attempt + 1)
                print(f"Rate limited (429). Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Failed. Status code: {response.status_code}. (Attempt {attempt+1}/{max_retries})")
                time.sleep(5)
        except Exception as e:
            print(f"Error: {e}. (Attempt {attempt+1}/{max_retries})")
            time.sleep(5)
    return False

def main():
    script_path = "script.md"
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    prompts = parse_prompts(script_path)
    for i, prompt in enumerate(prompts):
        filename = os.path.join(assets_dir, f"scene_{i+1}.jpg")
        if not os.path.exists(filename):
            print(f"\n--- Scene {i+1}/{len(prompts)} ---")
            success = download_image(prompt, filename)
            if success:
                # Be gentle to the free service
                time.sleep(2) 
            else:
                print(f"Failed to download {filename} after all retries.")
        else:
            print(f"File {filename} already exists, skipping.")

if __name__ == "__main__":
    main()
