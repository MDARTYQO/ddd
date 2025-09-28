from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image_imagen(prompt, num_images=1):
    try:
        client = genai.Client()
        
        print(f"שולח בקשה עם הפרומפט: {prompt}")
        print(f"מודל: imagen-4.0-generate-001")
        print(f"מספר תמונות: {num_images}")
        
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=num_images,
            )
        )
        
        print(f"התקבלה תגובה עם {len(response.generated_images)} תמונות")
        
        for i, generated_image in enumerate(response.generated_images):
            filename = f"imagen_output_{i+1}.png"
            
            # שמור את התמונה
            generated_image.image.save(filename)
            print(f"תמונה {i+1} נשמרה: {filename}")
            
            # אופציונלי - הצג את התמונה (אם אפשר)
            try:
                generated_image.image.show()
            except:
                print(f"לא ניתן להציג את התמונה {i+1} (אין GUI)")
        
        return True
        
    except Exception as e:
        print(f"\n=== פרטי השגיאה המלאים ===")
        print(f"סוג השגיאה: {type(e).__name__}")
        print(f"הודעת השגיאה: {str(e)}")
        
        # בדוק אם זה שגיאת HTTP ספציפית
        if hasattr(e, 'response'):
            print(f"\nפרטי HTTP Response:")
            print(f"Status Code: {e.response.status_code}")
            print(f"Content: {e.response.text}")
        
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt> [num_images]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    num_images = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # הגבל מספר תמונות למקסימום 4
    num_images = min(num_images, 4)
    
    print("=== מתחיל תהליך יצירת תמונה עם Imagen ===")
    success = generate_image_imagen(prompt, num_images)
    
    if success:
        print("=== התהליך הושלם בהצלחה ===")
    else:
        print("=== התהליך נכשל ===")
        sys.exit(1)
