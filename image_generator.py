from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image(prompt, filename="gemini-native-image.png"):
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(filename)
            print(f"הקובץ {filename} נוצר!")
            return
    print("לא התקבלה תמונה מה-API.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    prompt = sys.argv[1]
    generate_image(prompt)
