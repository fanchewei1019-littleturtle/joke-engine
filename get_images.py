import requests
import os
import json

def get_lexica_images(prompts, output_dir):
    for i, prompt in enumerate(prompts):
        print(f"Searching for prompt {i+1}: {prompt}")
        url = f"https://lexica.art/api/v1/search?q={prompt.replace(' ', '+')}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', [])
            if images:
                # Use the first image
                img_url = images[0].get('srcFull') or images[0].get('src')
                print(f"Found image URL: {img_url}")
                
                file_path = os.path.join(output_dir, f"scene_{i+1}.jpg")
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"Saved to {file_path}")
                else:
                    print(f"Failed to download image: {img_response.status_code}")
            else:
                print(f"No images found for prompt {i+1}")
        else:
            print(f"API request failed with status code {response.status_code}")

if __name__ == "__main__":
    prompts = [
        "A rusty old yard with a handwritten sign saying 'Talking Dog for Sale', realistic photography style.",
        "A gentlemanly Golden Retriever sitting on a wooden porch chair, wearing a small black bowtie, high-quality photograph.",
        "A Golden Retriever wearing a sharp black tuxedo, running through a White House hallway, cinematic action shot.",
        "A Golden Retriever carrying a red first-aid kit on its back, in the snowy Alps mountains, professional rescue scene photography.",
        "A Golden Retriever sitting proudly with many shiny military medals on its chest, formal award ceremony background.",
        "A person looking skeptical and annoyed, pointing at a dog sitting nearby, cozy living room interior.",
        "A Golden Retriever looking innocent and cute with big eyes, close-up portrait."
    ]
    output_dir = r"C:\Users\chewei\Desktop\littleturtle\joke_project\assets"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    get_lexica_images(prompts, output_dir)
