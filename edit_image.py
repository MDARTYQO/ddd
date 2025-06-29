import os
import requests
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def edit_image_with_gemini(image_url, prompt, output_filename="edited_image.png"):
    image = download_image(image_url)
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            new_image = Image.open(BytesIO(part.inline_data.data))
            new_image.save(output_filename)
            print(f"הקובץ {output_filename} נוצר!")
            return
    print("לא התקבלה תמונה מה-API.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python edit_image.py <image_url> <prompt>")
        sys.exit(1)
    image_url = sys.argv[1]
    prompt = sys.argv[2]
    edit_image_with_gemini(image_url, prompt)
