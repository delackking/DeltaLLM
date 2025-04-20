import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os

# Hugging Face Stable Diffusion API
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Single request to HF endpoint (runs in thread)
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

# Generate 4 images and save to /Data folder
async def generate_images(prompt: str) -> list:
    prompt_clean = prompt.replace(" ", "_").strip()
    os.makedirs("Data", exist_ok=True)

    tasks = []
    for i in range(1):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, High Resolution, seed = {randint(0, 999999)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)
    paths = []

    for i, image_bytes in enumerate(image_bytes_list):
        path = os.path.join("Data", f"{prompt_clean}_{i + 1}.jpg")
        with open(path, "wb") as f:
            f.write(image_bytes)
        paths.append(path)

    return paths

# Helper function to be called from Streamlit app
def generate_image_list(prompt: str) -> list:
    return asyncio.run(generate_images(prompt))
