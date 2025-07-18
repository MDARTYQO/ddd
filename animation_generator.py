import os
import sys
import argparse
from io import BytesIO
import numpy as np
from PIL import Image
from tqdm import tqdm
import google.generativeai as genai

class AnimationGenerator:
    def __init__(self, output_dir="output_animations"):
        """מאתחל את מחולל האנימציות"""
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # אתחול ה-API של Google
        genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
    def generate_frame(self, prompt, frame_num, total_frames, style="cartoon"):
        """מייצר פריים בודד"""
        # שיפור הפרומפט עם פרטי הפריים הנוכחי
        enhanced_prompt = (
            f"{prompt}, {style} style, "
            f"frame {frame_num+1} of {total_frames}, "
            "smooth animation, high detail, clean lines"
        )
        
        try:
            # יצירת תמונה באמצעות המודל
            response = self.model.generate_content(
                contents=enhanced_prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            # בדיקה אם התקבלה תמונה
            if hasattr(response, 'parts') and response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        return Image.open(BytesIO(part.inline_data.data))
            
            # אם לא מצאנו תמונה, ננסה דרך אחרת
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                return Image.open(BytesIO(part.inline_data.data))
        except Exception as e:
            print(f"שגיאה ביצירת פריים {frame_num}: {str(e)}")
            return None

    def interpolate_frames(self, frames, target_frames):
        """יוצר מעבר חלק בין הפריימים"""
        if not frames:
            return []
            
        if len(frames) >= target_frames:
            return frames[:target_frames]
            
        result = []
        frames = [np.array(img) for img in frames]
        
        for i in range(target_frames):
            pos = (i / (target_frames - 1)) * (len(frames) - 1)
            idx1 = int(np.floor(pos))
            idx2 = min(idx1 + 1, len(frames) - 1)
            alpha = pos - idx1
            
            if idx1 == idx2:
                blended = frames[idx1]
            else:
                frame1 = frames[idx1].astype(np.float32)
                frame2 = frames[idx2].astype(np.float32)
                blended = frame1 * (1 - alpha) + frame2 * alpha
                blended = np.clip(blended, 0, 255).astype(np.uint8)
            
            result.append(Image.fromarray(blended))
            
        return result

    def create_animation(self, prompt, num_keyframes=6, output_frames=24, fps=8, style="cartoon", output_name="animation"):
        """יוצר אנימציה מלאה"""
        print(f"יוצר {num_keyframes} פריימי מפתח...")
        keyframes = []
        
        # יצירת פריימי מפתח
        for i in tqdm(range(num_keyframes), desc="Generating keyframes"):
            frame = self.generate_frame(prompt, i, num_keyframes, style)
            if frame:
                keyframes.append(frame)
            else:
                print(f"שגיאה ביצירת פריים מפתח {i+1}")
                
        if not keyframes:
            print("לא נוצרו פריימים. בדוק את החיבור ל-API.")
            return None
            
        # יצירת מעבר חלק
        print("מייצר אנימציה חלקה...")
        frames = self.interpolate_frames(keyframes, output_frames)
        
        # שמירת האנימציה כ-GIF
        gif_path = os.path.join(self.output_dir, f"{output_name}.gif")
        
        try:
            frames[0].save(
                gif_path,
                save_all=True,
                append_images=frames[1:],
                duration=int(1000/fps),  # משך זמן במילישניות
                loop=0,  # 0 = לולאה אינסופית
                optimize=True,
                quality=90,
                disposal=2,
                transparency=0,
                dither=0,
                subrectangles=True
            )
            print(f"האנימציה נשמרה ב: {os.path.abspath(gif_path)}")
            return gif_path
            
        except Exception as e:
            print(f"שגיאה בשמירת האנימציה: {str(e)}")
            return None

def main():
    # הגדרת ארגומנטים של שורת הפקודה
    parser = argparse.ArgumentParser(description='יוצר אנימציות מ-Google Gemini')
    parser.add_argument('prompt', type=str, help='הטקסט שיתורגם לתמונה')
    parser.add_argument('--keyframes', type=int, default=6, help='מספר פריימי המפתח (מומלץ 4-8)')
    parser.add_argument('--frames', type=int, default=24, help='מספר הפריימים הסופי')
    parser.add_argument('--fps', type=int, default=8, help='פריימים לשנייה')
    parser.add_argument('--style', type=str, default="cartoon", 
                       choices=["cartoon", "anime", "watercolor", "pixel art", "3d render"],
                       help='סגנון האנימציה')
    parser.add_argument('--output', type=str, default="animation", help='שם הקובץ (ללא סיומת)')
    
    args = parser.parse_args()
    
    # יצירת מופע של מחולל האנימציות
    generator = AnimationGenerator()
    
    # יצירת האנימציה
    result = generator.create_animation(
        prompt=args.prompt,
        num_keyframes=args.keyframes,
        output_frames=args.frames,
        fps=args.fps,
        style=args.style,
        output_name=args.output
    )
    
    if not result:
        sys.exit(1)

if __name__ == "__main__":
    main()
