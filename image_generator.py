from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os
import time
import random

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image(prompt, filename="gemini-native-image.png", max_retries=5):
    client = genai.Client()
    
    for attempt in range(max_retries):
        try:
            print(f"ניסיון {attempt + 1} מתוך {max_retries}...")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=prompt,
                config=types.GenerateContentConfig(response_modalities=['IMAGE', 'TEXT'])
            )
            
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(filename)
                    print(f"הקובץ {filename} נוצר בהצלחה!")
                    return True
                    
            print("לא התקבלה תמונה מה-API.")
            return False
            
        except Exception as e:
            error_str = str(e)
            
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                if attempt < max_retries - 1:  # אם זה לא הניסיון האחרון
                    # Exponential backoff עם קצת רנדום
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    print(f"שגיאת rate limit - ממתין {wait_time:.1f} שניות...")
                    time.sleep(wait_time)
                else:
                    print("נכשל אחרי כל הניסיונות - יותר מדי בקשות")
                    return False
            else:
                print(f"שגיאה אחרת: {e}")
                return False
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    # הוסף השהיה קטנה בהתחלה למקרה שיש בקשות קודמות
    time.sleep(1)
    
    success = generate_image(prompt)
    if not success:
        print("יצירת התמונה נכשלה")
        sys.exit(1)
