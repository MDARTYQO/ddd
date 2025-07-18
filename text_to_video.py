import os
import requests
from PIL import Image
import numpy as np
import imageio
import time
import random
from io import BytesIO
import base64

# Configuration
STABILITY_API_KEY = "YOUR_STABILITY_API_KEY"  # You'll need to get this from stability.ai
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

def generate_image_with_stability(prompt, style, seed=42, width=512, height=512):
    """Generate an image using Stability AI API"""
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }
    
    data = {
        "prompt": f"{prompt}, {style}",
        "output_format": "png",
        "seed": seed,
        "width": width,
        "height": height,
        "samples": 1,
        "steps": 30
    }
    
    response = requests.post(
        url,
        headers=headers,
        files={"none": ''},  # Required by the API
        data=data
    )
    
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

def interpolate_frames(frames, num_frames):
    """Simple frame interpolation"""
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
    num_frames: int = 8,
    fps: int = 4,
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
    print("Starting video generation with Stability AI API...")
    start_time = time.time()
    
    if not STABILITY_API_KEY or STABILITY_API_KEY == "YOUR_STABILITY_API_KEY":
        raise ValueError("Please set your Stability AI API key in the STABILITY_API_KEY variable")
    
    # Set random seed for reproducibility
    random.seed(seed)
    np.random.seed(seed)
    
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
        try:
            image = generate_image_with_stability(
                prompt=frame_prompt,
                style=style,
                seed=seed + i,
                width=width,
                height=height
            )
            keyframes.append(np.array(image))
        except Exception as e:
            print(f"Error generating frame {i+1}: {str(e)}")
            if keyframes:  # If we have at least one frame, duplicate it
                keyframes.append(keyframes[-1])
            else:
                # Create a blank frame if we can't generate any images
                keyframes.append(np.zeros((height, width, 3), dtype=np.uint8))
    
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
