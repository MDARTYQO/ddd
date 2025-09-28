from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyCpEuS3QQflHCzj-CB3FtvOPT_lXZvlycI"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image_safe(prompt, filename="gemini-native-image.png"):
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
        
        # בדיקה מפורטת של מבנה התגובה
        print(f"סוג התגובה: {type(response)}")
        print(f"יש candidates? {hasattr(response, 'candidates')}")
        
        if not hasattr(response, 'candidates') or not response.candidates:
            print("אין candidates בתגובה")
            return False
        
        print(f"מספר candidates: {len(response.candidates)}")
        
        candidate = response.candidates[0]
        print(f"סוג candidate: {type(candidate)}")
        print(f"יש content? {hasattr(candidate, 'content')}")
        
        if not hasattr(candidate, 'content') or candidate.content is None:
            print("אין content ב-candidate")
            return False
        
        content = candidate.content
        print(f"סוג content: {type(content)}")
        print(f"יש parts? {hasattr(content, 'parts')}")
        
        if not hasattr(content, 'parts') or content.parts is None:
            print("אין parts ב-content")
            return False
        
        print(f"מספר parts: {len(content.parts)}")
        
        for i, part in enumerate(content.parts):
            print(f"Part {i + 1}: {type(part)}")
            
            if hasattr(part, 'text') and part.text is not None:
                print(f"  טקסט: {part.text}")
            elif hasattr(part, 'inline_data') and part.inline_data is not None:
                print(f"  נתוני תמונה: {len(part.inline_data.data)} bytes")
                print(f"  MIME type: {part.inline_data.mime_type}")
                
                try:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(filename)
                    print(f"התמונה נשמרה בהצלחה: {filename}")
                    return True
                except Exception as img_error:
                    print(f"שגיאה בשמירת התמונה: {img_error}")
            else:
                print(f"  Part לא מזוהה: {dir(part)}")
        
        print("לא נמצאו נתוני תמונה בתגובה")
        return False
        
    except Exception as e:
        print(f"שגיאה כללית: {e}")
        print(f"סוג השגיאה: {type(e)}")
        
        # הדפס מידע נוסף על השגיאה
        import traceback
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("=== מתחיל יצירת תמונה עם בדיקות מפורטות ===")
    success = generate_image_safe(prompt)
    
    if success:
        print("=== התהליך הושלם בהצלחה! ===")
    else:
        print("=== התהליך נכשל ===")
        sys.exit(1)
