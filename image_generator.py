from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image_working(prompt, filename="generated_image.png"):
    try:
        client = genai.Client()
        
        print(f"שולח בקשה עם הפרומפט: {prompt}")
        print("מודל: gemini-2.0-flash-exp-image-generation")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[prompt],
            config=types.GenerateContentConfig(response_modalities=['IMAGE', 'TEXT'])
        )
        
        print("התקבלה תגובה מהשרת")
        
        for i, part in enumerate(response.candidates[0].content.parts):
            if part.text is not None:
                print(f"טקסט: {part.text}")
            elif part.inline_data is not None:
                print(f"נמצאו נתוני תמונה: {len(part.inline_data.data)} bytes")
                
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filename)
                print(f"התמונה נשמרה בהצלחה: {filename}")
                return True
        
        print("לא נמצאו נתוני תמונה בתגובה")
        return False
        
    except Exception as e:
        print(f"שגיאה: {e}")
        
        # אם המודל הראשון נכשל, נסה את השני
        if "gemini-2.0-flash-exp-image-generation" in str(e):
            print("מנסה מודל חלופי...")
            return try_alternative_model(prompt, filename)
        
        return False

def try_alternative_model(prompt, filename):
    try:
        client = genai.Client()
        
        print("מנסה מודל: gemini-2.0-flash-preview-image-generation")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[prompt],
            config=types.GenerateContentConfig(response_modalities=['IMAGE', 'TEXT'])
        )
        
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filename)
                print(f"התמונה נשמרה בהצלחה עם המודל החלופי: {filename}")
                return True
        
        return False
        
    except Exception as e:
        print(f"גם המודל החלופי נכשל: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("=== מתחיל יצירת תמונה עם המודלים הזמינים ===")
    success = generate_image_working(prompt)
    
    if success:
        print("=== התהליך הושלם בהצלחה! ===")
    else:
        print("=== התהליך נכשל ===")
        sys.exit(1)
