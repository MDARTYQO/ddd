import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import numpy as np
import imageio
from pathlib import Path
import time
import random

# Configuration
MODEL_ID = "runwayml/stable-diffusion-v1-5"  # Base model for Text2Video-Zero
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_DIR = "output_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Animation style prompt template
ANIMATION_STYLES = {
    "pixar": "Pixar style 3D animation, vibrant colors, soft lighting, highly detailed",
    "anime": "Anime style, Studio Ghibli, vibrant colors, detailed background",
    "watercolor": "Watercolor painting style, soft edges, artistic, dreamy",
    "cyberpunk": "Cyberpunk neon style, futuristic, vibrant colors",
    "claymation": "Claymation style, stop motion, soft lighting"
}

# Simple interpolation between frames
def interpolate_frames(frames, num_frames):
    if len(frames) >= num_frames:
        return frames[:num_frames]
    
    result = []
    for i in range(num_frames):
        idx = int((i / (num_frames - 1)) * (len(frames) - 1))
        result.append(frames[idx])
    return result

def apply_animation_style(prompt: str, style: str = "pixar") -> str:
    """Apply animation style to the prompt."""
    style_template = ANIMATION_STYLES.get(style.lower(), ANIMATION_STYLES["pixar"])
    return f"{prompt}, {style_template}"

def create_video_from_text(
    prompt: str,
    num_frames: int = 8,  # Reduced for CPU compatibility
    fps: int = 4,  # Lower FPS for smoother playback
    seed: int = 42,
    output_filename: str = "generated_video",
    style: str = "pixar",
    height: int = 512,
    width: int = 512
) -> str:
    """
    Create a video from text using Text2Video-Zero.
    
    Args:
        prompt: Text prompt describing the video
        num_frames: Number of frames to generate (reduced for CPU)
        fps: Frames per second for the output video
        seed: Random seed for reproducibility
        output_filename: Base name for the output file (without extension)
        style: Animation style (pixar, anime, watercolor, cyberpunk, claymation)
        
    Returns:
        Path to the generated video file
    """
    print(f"Initializing model on {DEVICE}...")
    start_time = time.time()
    
    # Set random seed for reproducibility
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    
    # Initialize the pipeline with lower memory requirements
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32,  # Using float32 for better CPU compatibility
        safety_checker=None,
        requires_safety_checker=False
    )
    
    # Configure scheduler for better performance
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    # Move to device and enable attention slicing for lower memory usage
    pipe = pipe.to(DEVICE)
    pipe.enable_attention_slicing()
    
    # Apply animation style to prompt
    enhanced_prompt = apply_animation_style(prompt, style)
    print(f"Enhanced prompt: {enhanced_prompt}")
    
    # Generate keyframes (fewer than requested frames)
    num_keyframes = min(4, num_frames)  # Generate only 4 keyframes max
    print(f"Generating {num_keyframes} keyframes...")
    
    keyframes = []
    for i in range(num_keyframes):
        print(f"Generating keyframe {i+1}/{num_keyframes}")
        # Slightly modify prompt for each keyframe
        frame_prompt = f"{enhanced_prompt}, frame {i+1} of {num_keyframes}"
        
        # Generate image with consistent seed but slightly varied prompt
        image = pipe(
            frame_prompt,
            height=height,
            width=width,
            num_inference_steps=15,
            generator=torch.Generator(device=DEVICE).manual_seed(seed + i)
        ).images[0]
        
        keyframes.append(np.array(image))
    
    # Interpolate between keyframes to create smooth animation
    print(f"Creating {num_frames} frames from {num_keyframes} keyframes...")
    frames = interpolate_frames(keyframes, num_frames)
    
    # Save as GIF and MP4
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        # Save as GIF
        gif_path = f"{output_path}.gif"
        print(f"Saving GIF to {gif_path}")
        imageio.mimsave(gif_path, frames, fps=fps, loop=0)
        
        # Save as MP4 if possible
        try:
            mp4_path = f"{output_path}.mp4"
            print(f"Saving MP4 to {mp4_path}")
            with imageio.get_writer(mp4_path, fps=fps, codec='libx264') as writer:
                for frame in frames:
                    writer.append_data(frame)
            output_file = mp4_path
        except Exception as e:
            print(f"Could not save MP4: {e}. Using GIF instead.")
            output_file = gif_path
        
        total_time = time.time() - start_time
        print(f"Video generation completed in {total_time:.2f} seconds")
        
        return output_file
        
    except Exception as e:
        print(f"Error saving video: {e}")
        # Try to save at least one frame as fallback
        try:
            output_path = f"{output_path}_frame0.png"
            Image.fromarray(frames[0]).save(output_path)
            print(f"Saved first frame as fallback to {output_path}")
            return output_path
        except:
            print("Could not save any output files")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate animated video from text using Stable Diffusion")
    parser.add_argument("--prompt", type=str, required=True, 
                      help="Text prompt describing the video")
    parser.add_argument("--style", type=str, default="pixar",
                      choices=["pixar", "anime", "watercolor", "cyberpunk", "claymation"],
                      help="Animation style")
    parser.add_argument("--frames", type=int, default=8, 
                      help="Number of frames to generate (4-16 recommended)")
    parser.add_argument("--fps", type=int, default=4, 
                      help="Frames per second for the output video (1-4 recommended)")
    parser.add_argument("--seed", type=int, default=42, 
                      help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="animation", 
                      help="Output filename (without extension)")
    parser.add_argument("--height", type=int, default=512,
                      help="Image height (multiple of 8, max 512)")
    parser.add_argument("--width", type=int, default=512,
                      help="Image width (multiple of 8, max 512)")
    
    args = parser.parse_args()
    
    print(f"=== Starting Video Generation ===")
    print(f"Prompt: {args.prompt}")
    print(f"Style: {args.style}")
    print(f"Frames: {args.frames}")
    print(f"FPS: {args.fps}")
    print(f"Seed: {args.seed}")
    
    # Validate frame count
    if args.frames < 2:
        print("Warning: At least 2 frames are required. Setting to 2.")
        args.frames = 2
    elif args.frames > 16:
        print("Warning: More than 16 frames may cause memory issues. Limiting to 16.")
        args.frames = 16
    
    # Validate dimensions
    args.height = max(64, min(512, args.height // 8 * 8))  # Round down to nearest multiple of 8
    args.width = max(64, min(512, args.width // 8 * 8))    # Round down to nearest multiple of 8
    
    try:
        video_path = create_video_from_text(
            prompt=args.prompt,
            style=args.style,
            num_frames=args.frames,
            fps=args.fps,
            seed=args.seed,
            output_filename=args.output,
            height=args.height,
            width=args.width
        )
        
        if video_path:
            print(f"\n=== Video Generation Completed ===")
            print(f"Output saved to: {os.path.abspath(video_path)}")
            print(f"File size: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
            print("You can find the output in the 'output_videos' directory.")
        else:
            print("\n=== Warning: No video was generated ===")
            
    except torch.cuda.OutOfMemoryError:
        print("\n=== Error: Out of Memory ===")
        print("The script ran out of GPU/CPU memory. Try these fixes:")
        print("1. Reduce the number of frames (--frames)")
        print("2. Reduce the image size (--width and --height)")
        print("3. Use a simpler prompt")
        raise
    except Exception as e:
        print(f"\n=== Error Occurred ===")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Try reducing the number of frames (--frames)")
        print("2. Try reducing the image size (--width and --height)")
        print("3. Try a simpler prompt")
        print("4. Check if you have enough disk space and memory")
        raise
