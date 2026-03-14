import os
import re
import requests
import time
import random

def parse_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match Image Prompt lines
    prompts = re.findall(r'- \*\*Image Prompt\*\*: (.+)', content)
    return prompts

def download_image(prompt, filename):
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(1, 100000)
    # Encode prompt for URL
    encoded_prompt = requests.utils.quote(prompt)
    # Simpler URL, no extra parameters that might cause 500
    url = f"{base_url}{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
    
    print(f"Downloading: {filename} for prompt: {prompt[:50]}... (Seed: {seed})")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Short timeout, Pollinations is usually fast if it's working
            response = requests.get(url, timeout=30) 
            if response.status_code == 200:
                # Check if it's actually an image
                if response.headers.get('Content-Type', '').startswith('image'):
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Successfully saved to {filename}")
                    return True
                else:
                    print(f"Response not an image: {response.headers.get('Content-Type')}")
            elif response.status_code == 429:
                print(f"Rate limited (429). Waiting longer... (Attempt {attempt+1}/{max_retries})")
                time.sleep(15 * (attempt + 1))
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
            success = download_image(prompt, filename)
            if success:
                # Add a small delay to be nice to the server
                time.sleep(3)
            else:
                print(f"Failed to download {filename} after retries.")
        else:
            print(f"File {filename} already exists, skipping.")

if __name__ == "__main__":
    main()
