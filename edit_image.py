import os
import requests
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def load_image(image_input):
    """Load an image from either a URL or a local file path."""
    if image_input.startswith(('http://', 'https://')):
        # It's a URL
        response = requests.get(image_input)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    else:
        # It's a local file path
        return Image.open(image_input)

def edit_image_with_gemini(image_input, prompt, output_filename="edited_image.png"):
    """Edit an image using Gemini.
    
    Args:
        image_input: Either a URL (starting with http/https) or a local file path
        prompt: The editing instruction
        output_filename: Where to save the result
    """
    image = load_image(image_input)
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
        print("Usage: python edit_image.py <image_path_or_url> <prompt>")
        sys.exit(1)
    
    image_input = sys.argv[1]
    prompt = sys.argv[2]
    edit_image_with_gemini(image_input, prompt)
