from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image_with_person(prompt, filename="gemini-native-image.png"):
    try:
        client = genai.Client()
        
        print(f"שולח בקשה עם הפרומפט: {prompt}")
        print("מודל: gemini-2.0-flash-exp-image-generation")
        print("מאפשר יצירת אנשים: allow_adult")
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT'],
                # הוספת הגדרות מתקדמות
                generation_config=types.GenerationConfig(
                    # פרמטרים ליצירת תמונות
                    response_mime_type="image/png"
                ),
                # הגדרות ליצירת אנשים
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH
                    )
                ]
            )
        )
        
        print("התקבלה תגובה מהשרת")
        
        candidate = response.candidates[0]
        
        # בדוק finish_reason
        if hasattr(candidate, 'finish_reason'):
            print(f"Finish reason: {candidate.finish_reason}")
        
        if candidate.content is None:
            print("Content הוא None - הבקשה נדחתה")
            return False
        
        for i, part in enumerate(candidate.content.parts):
            print(f"Part {i + 1}: {type(part)}")
            
            if hasattr(part, 'text') and part.text is not None:
                print(f"  טקסט: {part.text}")
            elif hasattr(part, 'inline_data') and part.inline_data is not None:
                print(f"  נתוני תמונה: {len(part.inline_data.data)} bytes")
                
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filename)
                print(f"התמונה נשמרה בהצלחה: {filename}")
                return True
        
        return False
        
    except Exception as e:
        print(f"שגיאה: {e}")
        return False

def try_imagen_api(prompt, filename="gemini-native-image.png"):
    """נסה עם Imagen API עם הגדרות מתקדמות"""
    try:
        client = genai.Client()
        
        print(f"מנסה Imagen עם הפרומפט: {prompt}")
        
        # נסה עם Imagen API
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                # הגדרות מתקדמות
                person_generation="allow_adult",  # מאפשר יצירת מבוגרים
                aspect_ratio="1:1",
                image_size="1K"
            )
        )
        
        print("התקבלה תגובה מ-Imagen")
        
        if response.generated_images:
            generated_image = response.generated_images[0]
            generated_image.image.save(filename)
            print(f"התמונה נשמרה עם Imagen: {filename}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Imagen נכשל: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("=== מנסה עם הגדרות מתקדמות לאנשים ===")
    
    # נסה קודם עם Gemini
    success = generate_image_with_person(prompt)
    
    if not success:
        print("\n=== מנסה עם Imagen API ===")
        success = try_imagen_api(prompt)
    
    if success:
        print("=== התהליך הושלם בהצלחה! ===")
    else:
        print("=== כל הניסיונות נכשלו ===")
        sys.exit(1)
