import google.generativeai as genai
import os
import base64
import time

# --- הגדרת מפתח ה-API (מוטמע ישירות - לא מומלץ לאבטחה!) ---
# אנא החלף את "הכנס_כאן_את_מפתח_ה_API_שלך" במפתח ה-API האמיתי שלך.
# שים לב: הטמעת מפתח API ישירות בקוד חושפת אותו לכל מי שיש לו גישה לקוד.
GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"

genai.configure(api_key=API_KEY)

# --- בחירת המודל ליצירת מוזיקה ---
# ודא שהמודל 'gemini-1.5-flash-music-001' זמין באזור שלך.
MODEL_NAME = 'models/gemini-1.5-flash-music-001'

try:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"המודל '{MODEL_NAME}' נטען בהצלחה.")
except Exception as e:
    print(f"שגיאה בטעינת המודל '{MODEL_NAME}': {e}")
    print("אנא ודא שהמודל זמין עבור מפתח ה-API שלך.")
    exit()

# --- הגדרת הפרומפט (תיאור השיר) ---
# שנה את הטקסט הזה כדי לתאר את המוזיקה שברצונך ליצור.
prompt_text = "צור טרק מוזיקלי אלקטרוני מקפיץ, עם סינתיסייזרים בהירים, קצב דאנס מהיר (כ-130 BPM), ובאס ליין עמוק. מתאים לאווירת מסיבה אנרגטית."

print(f"\nשולח בקשה ליצירת טרק מוזיקלי עם התיאור:\n'{prompt_text}'")

try:
    # --- שליחת הבקשה למודל ---
    response = model.generate_content(prompt_text)

    # --- עיבוד התגובה ושמירת האודיו ---
    audio_part = None
    if response and response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'audio_data') and part.audio_data and part.audio_data.data:
                audio_part = part.audio_data
                break

    if audio_part:
        audio_data_base64 = audio_part.data
        audio_bytes = base64.b64decode(audio_data_base64)

        timestamp = int(time.time())
        output_filename = f"generated_track_{timestamp}.mp3"

        with open(output_filename, "wb") as f:
            f.write(audio_bytes)

        print(f"\n✅ הטרק נוצר בהצלחה ונשמר כקובץ: {output_filename}")
        print("הקובץ נוצר בסביבת הריצה של GitHub Actions.")

    else:
        print("\n❌ שגיאה: התגובה מהמודל לא הכילה נתוני אודיו.")
        if response and response.prompt_feedback:
             print("משוב מהמודל:", response.prompt_feedback)
        if response and response.candidates and response.candidates[0].finish_reason:
             print("סיבת סיום:", response.candidates[0].finish_reason)
        if response and response.candidates and response.candidates[0].safety_ratings:
             print("דירוגי בטיחות:", response.candidates[0].safety_ratings)


except Exception as e:
    print(f"\n❌ אירעה שגיאה במהלך יצירת הטרק: {e}")
