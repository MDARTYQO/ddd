import requests
import sys

def generate_image(prompt, filename="image.png"):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"accept": "image/png"}
    data = {"inputs": prompt}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"הקובץ {filename} נוצר!")
    else:
        print("שגיאה ביצירת תמונה:", response.status_code, response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    prompt = sys.argv[1]
    generate_image(prompt)
