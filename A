
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import sys
import os

GOOGLE_API_KEY = "AIzaSyBXphJJz9ygt1Jorl15H82HmSgiSyTk7AM"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def generate_image_simple(prompt, filename="gemini-native-image.png"):
    try:
        client = genai.Client()
        
        print(f"שולח בקשה עם הפרומפט: {prompt}")
        print("מודל: gemini-2.0-flash-exp-image-generation")
        
        # קוד פשוט יותר בלי הגדרות מסובכות
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
        )
        
        print("התקבלה תגובה מהשרת")
        
        candidate = response.candidates[0]
        
        # בדוק finish_reason
        if hasattr(candidate, 'finish_reason'):
            print(f"Finish reason: {candidate.finish_reason}")
        
        # בדוק safety ratings
        if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
            print("Safety ratings:")
            for rating in candidate.safety_ratings:
                print(f"  {rating.category}: {rating.probability}")
        
        if candidate.content is None:
            print("Content הוא None - הבקשה נדחתה כנראה בגלל content policy")
            
            # נסה פרומפט מעודן
            refined_prompt = refine_prompt(prompt)
            if refined_prompt != prompt:
                print(f"מנסה פרומפט מעודן: {refined_prompt}")
                return generate_image_simple(refined_prompt, filename)
            
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

def refine_prompt(original_prompt):
    """מעדן פרומפטים בעייתיים"""
    
    # החלפות לפרומפטים יותר מקובלים
    replacements = {
        "emma watson": "young woman with short brown hair",
        "lingerie": "elegant fashion",
        "underwear": "stylish clothing",
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    }
    
    refined = original_prompt.lower()
    
    for old, new in replacements.items():
        if old in refined:
            refined = refined.replace(old, new)
            print(f"החלפתי '{old}' ב-'{new}'")
    
    return refined

def try_safe_alternatives():
    """נסה כמה אלטרנטיבות בטוחות"""
    
    safe_prompts = [
        "A portrait of an elegant young woman with short brown hair in sophisticated fashion",
        "Beautiful actress in classic Hollywood glamour style",
        "Woman with Emma Watson's hairstyle in vintage elegant dress",
        "Portrait of a confident woman in fashionable attire"
    ]
    
    for i, prompt in enumerate(safe_prompts):
        print(f"\n=== מנסה אלטרנטיבה {i+1}: {prompt} ===")
        success = generate_image_simple(prompt, f"alternative_{i+1}.png")
        if success:
            print(f"✅ אלטרנטיבה {i+1} עבדה!")
            return True
    
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py <prompt>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    print("=== מנסה את הפרומפט המקורי ===")
    success = generate_image_simple(prompt)
    
    if not success:
        print("\n=== הפרומפט המקורי נכשל, מנסה אלטרנטיבות בטוחות ===")
        success = try_safe_alternatives()
    
    if success:
        print("=== התהליך הושלם בהצלחה! ===")
    else:
        print("=== כל הניסיונות נכשלו ===")
        sys.exit(1)
