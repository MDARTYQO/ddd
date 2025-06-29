import requests
import base64
import sys
import os

GEMINI_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"

def generate_image(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"]
        }
    }
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()
    parts = data['candidates'][0]['content']['parts']
    image_part = next((p for p in parts if 'inlineData' in p), None)
    if not image_part:
        raise Exception("לא התקבלה תמונה מה-API. ייתכן שיש בעיה בהנחיה או במפתח.")
    b64 = image_part['inlineData']['data']
    image_bytes = base64.b64decode(b64)
    return image_bytes

def main():
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    prompt = sys.argv[1]
    print("יוצר תמונה...")
    image = generate_image(prompt, GEMINI_API_KEY)
    with open("image.png", "wb") as f:
        f.write(image)
    print("הקובץ image.png נוצר!")

if __name__ == "__main__":
    main()
