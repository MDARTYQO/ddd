from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os
import traceback

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image(prompt, filename="generated_image.png"):
    try:
        client = genai.Client()
        
        print(f"שולח בקשה עם הפרומפט: {prompt}")
        print("מודל: gemini-2.5-flash-image-preview")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
        )
        
        print("התקבלה תגובה מהשרת")
        print(f"מספר מועמדים: {len(response.candidates)}")
        
        if not response.candidates:
            print("אין מועמדים בתגובה")
            return False
            
        candidate = response.candidates[0]
        print(f"מספר חלקים במועמד הראשון: {len(candidate.content.parts)}")
        
        for i, part in enumerate(candidate.content.parts):
            print(f"חלק {i + 1}:")
            
            if part.text is not None:
                print(f"  טקסט: {part.text}")
            elif part.inline_data is not None:
                print(f"  נתונים inline: {len(part.inline_data.data)} bytes")
                print(f"  סוג MIME: {part.inline_data.mime_type}")
                
                try:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(filename)
                    print(f"  התמונה נשמרה בהצלחה: {filename}")
                    return True
                except Exception as img_error:
                    print(f"  שגיאה בשמירת התמונה: {img_error}")
                    return False
            else:
                print(f"  חלק לא מזוהה: {type(part)}")
        
        print("לא נמצאו נתוני תמונה בתגובה")
        return False
        
    except Exception as e:
        print(f"\n=== פרטי השגיאה המלאים ===")
        print(f"סוג השגיאה: {type(e).__name__}")
        print(f"הודעת השגיאה: {str(e)}")
        
        # הדפס את כל המידע הטכני
        print(f"\nStack trace מלא:")
        traceback.print_exc()
        
        # בדוק אם זה שגיאת HTTP ספציפית
        if hasattr(e, 'response'):
            print(f"\nפרטי HTTP Response:")
            print(f"Status Code: {e.response.status_code}")
            print(f"Headers: {dict(e.response.headers)}")
            print(f"Content: {e.response.text}")
        
        # בדוק אם יש מידע נוסף על השגיאה
        if hasattr(e, 'details'):
            print(f"\nפרטים נוספים: {e.details}")
            
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("=== מתחיל תהליך יצירת תמונה ===")
    success = generate_image(prompt)
    
    if success:
        print("=== התהליך הושלם בהצלחה ===")
    else:
        print("=== התהליך נכשל ===")
        sys.exit(1)
