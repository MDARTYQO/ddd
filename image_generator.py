from google import genai
import os

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def check_quota_and_models():
    try:
        client = genai.Client()
        
        print("=== בדיקת מודלים זמינים ===")
        models = client.models.list()
        
        text_models = []
        image_models = []
        
        for model in models:
            model_name = model.name
            print(f"מודל: {model_name}")
            
            if "image" in model_name.lower() or "imagen" in model_name.lower():
                image_models.append(model_name)
                print("  ^ מודל תמונות")
            elif "text" in model_name.lower() or "flash" in model_name.lower() or "pro" in model_name.lower():
                text_models.append(model_name)
                print("  ^ מודל טקסט")
        
        print(f"\n=== סיכום ===")
        print(f"מודלי טקסט זמינים: {len(text_models)}")
        for model in text_models:
            print(f"  - {model}")
            
        print(f"\nמודלי תמונות זמינים: {len(image_models)}")
        for model in image_models:
            print(f"  - {model}")
        
        # נסה בקשה פשוטה לטקסט כדי לבדוק אם ה-API Key עובד בכלל
        print(f"\n=== בדיקת API Key עם בקשת טקסט פשוטה ===")
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=["Say hello in Hebrew"]
            )
            print("✅ API Key עובד - תגובה:")
            print(response.candidates[0].content.parts[0].text)
        except Exception as text_error:
            print(f"❌ גם בקשות טקסט לא עובדות: {text_error}")
        
    except Exception as e:
        print(f"שגיאה בבדיקת מודלים: {e}")

if __name__ == "__main__":
    check_quota_and_models()
