import os
import requests
import time

def download_image(keywords, filename):
    url = f"https://loremflickr.com/1280/720/{keywords}"
    print(f"Downloading: {filename} with keywords: {keywords}")
    try:
        response = requests.get(url, timeout=30)
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
    keywords_list = ["dog,pizza", "dog,angry", "dog,calculator", "dog,sunglasses"]
    for i, kw in enumerate(keywords_list):
        download_image(kw, os.path.join(assets_dir, f"scene_{i+1}.jpg"))
        time.sleep(1)
