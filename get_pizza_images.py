import os
import requests
import random
from urllib.parse import quote
import time

def download_image(prompt, filename):
    base_url = "https://image.pollinations.ai/prompt/"
    seed = random.randint(1, 1000000)
    enhanced_prompt = f"{prompt}, highly detailed, 8k, cinematic lighting"
    encoded_prompt = quote(enhanced_prompt)
    url = f"{base_url}{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true"
    print(f"Downloading: {filename} with prompt: {prompt}")
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    assets_dir = r"C:\Users\chewei\Desktop\littleturtle\joke_project\assets_pizza"
    os.makedirs(assets_dir, exist_ok=True)
    prompts = [
        "A cute golden retriever sitting at a dining table, staring intensely at a large, delicious pepperoni pizza in a box, cinematic style.",
        "An angry owner pointing to a bowl of dry dog food next to a golden retriever who looks disappointed, dining room background.",
        "A golden retriever using a calculator with its paw, a pizza on the table, owner looking surprised in the background.",
        "A golden retriever wearing sunglasses and a gold chain, looking cool, holding a smartphone in its paw, owner looking shocked in the background, pizza box on the table."
    ]
    for i, p in enumerate(prompts):
        download_image(p, os.path.join(assets_dir, f"scene_{i+1}.jpg"))
        time.sleep(2)
