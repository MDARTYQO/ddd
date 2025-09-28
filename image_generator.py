
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyBXphJJz9ygt1Jorl15H82HmSgiSyTk7AM"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image_clean(prompt, filename="gemini-native-image.png"):
    try:
        client = genai.Client()
        
        print(f"שולח בקשה עם הפרומפט: {prompt}")
        print("מודל: gemini-2.0-flash-exp-image-generation")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
        )
        
        print("התקבלה תגובה מהשרת")
        
        candidate = response.candidates[0]
        
        if hasattr(candidate, 'finish_reason'):
            print(f"Finish reason: {candidate.finish_reason}")
        
        if candidate.content is None:
            print("Content הוא None - הבקשה נדחתה")
            return False
        
        for i, part in enumerate(candidate.content.parts):
            if hasattr(part, 'text') and part.text is not None:
                print(f"טקסט: {part.text}")
            elif hasattr(part, 'inline_data') and part.inline_data is not None:
                print(f"נתוני תמונה: {len(part.inline_data.data)} bytes")
                
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filename)
                print(f"התמונה נשמרה בהצלחה: {filename}")
                return True
        
        return False
        
    except Exception as e:
        print(f"שגיאה: {e}")
        return False

def try_alternative_model(prompt, filename="gemini-native-image.png"):
    """נסה מודל אחר"""
    try:
        client = genai.Client()
        
        print("מנסה מודל חלופי: gemini-2.0-flash-preview-image-generation")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
        )
        
        candidate = response.candidates[0]
        
        if candidate.content is None:
            print("גם המודל החלופי דחה את הבקשה")
            return False
        
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filename)
                print(f"התמונה נשמרה עם המודל החלופי: {filename}")
                return True
        
        return False
        
    except Exception as e:
        print(f"המודל החלופי נכשל: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("=== מנסה מודל ראשי ===")
    success = generate_image_clean(prompt)
    
    if not success:
        print("\n=== מנסה מודל חלופי ===")
        success = try_alternative_model(prompt)
    
    if success:
        print("=== התהליך הושלם בהצלחה! ===")
    else:
        print("=== כל הניסיונות נכשלו ===")
        sys.exit(1)
