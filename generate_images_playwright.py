# -*- coding: utf-8 -*-
import os
import re
import asyncio
import requests
from playwright.async_api import async_playwright

def parse_prompts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    prompts = re.findall(r'- \*\*Image Prompt\*\*: (.+)', content)
    return prompts

async def download_image_playwright(prompt, filename):
    base_url = "https://image.pollinations.ai/prompt/"
    encoded_prompt = requests.utils.quote(prompt)
    url = f"{base_url}{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    print(f"Downloading: {filename} for prompt: {prompt[:50]}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # Set a long timeout
            response = await page.goto(url, timeout=60000)
            if response and response.status == 200:
                body = await response.body()
                with open(filename, 'wb') as f:
                    f.write(body)
                print(f"Successfully saved to {filename}")
                await browser.close()
                return True
            else:
                print(f"Failed to download. Status: {response.status if response else 'None'}")
        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()
    return False

async def main():
    script_path = "script.md"
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    prompts = parse_prompts(script_path)
    for i, prompt in enumerate(prompts):
        filename = os.path.join(assets_dir, f"scene_{i+1}.jpg")
        if not os.path.exists(filename):
            success = await download_image_playwright(prompt, filename)
            if success:
                await asyncio.sleep(5)
            else:
                print(f"Failed to download {filename}")
        else:
            print(f"File {filename} already exists, skipping.")

if __name__ == "__main__":
    asyncio.run(main())
