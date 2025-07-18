from google import genai
from google.genai import types
from PIL import Image, ImageSequence
from io import BytesIO
import os
import numpy as np
from tqdm import tqdm
import argparse
import sys

# הגדרת משתני סביבה
GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

class AnimationGenerator:
    def __init__(self, output_dir="output_animations"):
        self.client = genai.Client()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_frame(self, prompt, frame_num, total_frames, style="cartoon"):
        """יוצר פריים בודד עם פרומפט מותאם"""
        enhanced_prompt = (
            f"{prompt}, {style} style, "
            f"frame {frame_num+1} of {total_frames}, "
            f"smooth animation, high detail, clean lines"
        )
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE'],
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "candidate_count": 1
                    }
                )
            )
            
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return Image.open(BytesIO(part.inline_data.data))
                    
        except Exception as e:
            print(f"שגיאה ביצירת פריים {frame_num}: {str(e)}")
            return None

    def interpolate_frames(self, frames, target_frames):
        """יוצר מעבר חלק בין הפריימים"""
        if not frames or len(frames) >= target_frames:
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
                
        if not keyframes:
            print("לא נוצרו פריימים. בדוק את החיבור ל-API.")
            return
            
        # יצירת מעבר חלק
        print("מייצר אנימציה חלקה...")
        frames = self.interpolate_frames(keyframes, output_frames)
        
        # שמירת האנימציה כ-GIF
        gif_path = os.path.join(self.output_dir, f"{output_name}.gif")
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=int(1000/fps),
            loop=0,
            optimize=True,
            quality=90
        )
        
        print(f"האנימציה נשמרה ב: {os.path.abspath(gif_path)}")
        return gif_path

def main():
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
    
    generator = AnimationGenerator()
    generator.create_animation(
        prompt=args.prompt,
        num_keyframes=args.keyframes,
        output_frames=args.frames,
        fps=args.fps,
        style=args.style,
        output_name=args.output
    )

if __name__ == "__main__":
    main()
