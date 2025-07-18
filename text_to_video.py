import os
import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import numpy as np
import imageio
from pathlib import Path
import time
from typing import List, Optional, Union

# Configuration
MODEL_ID = "runwayml/stable-diffusion-v1-5"  # Base model for Text2Video-Zero
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_DIR = "output_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Animation style prompt template
ANIMATION_STYLES = {
    "pixar": "Pixar style 3D animation, vibrant colors, soft lighting, highly detailed, 4k",
    "anime": "Anime style, Studio Ghibli, vibrant colors, detailed background, 4k",
    "watercolor": "Watercolor painting style, soft edges, artistic, dreamy, 4k",
    "cyberpunk": "Cyberpunk neon style, futuristic, vibrant colors, 4k",
    "claymation": "Claymation style, stop motion, soft lighting, 4k"
}

def apply_animation_style(prompt: str, style: str = "pixar") -> str:
    """Apply animation style to the prompt."""
    style_template = ANIMATION_STYLES.get(style.lower(), ANIMATION_STYLES["pixar"])
    return f"{prompt}, {style_template}"

def create_video_from_text(
    prompt: str,
    num_frames: int = 16,  # Reduced for CPU compatibility
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
    
    # Initialize the pipeline with lower memory requirements
    pipe = DiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,  # Using float32 for better CPU compatibility
        safety_checker=None
    )
    
    # Configure scheduler for better performance
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    # Move to device and enable attention slicing for lower memory usage
    pipe = pipe.to(DEVICE)
    pipe.enable_attention_slicing()
    
    # Apply animation style to prompt
    enhanced_prompt = apply_animation_style(prompt, style)
    print(f"Enhanced prompt: {enhanced_prompt}")
    
    # Generate frames one by one to save memory
    print(f"Generating {num_frames} frames...")
    frames = []
    
    # Set seed for reproducibility
    generator = torch.Generator(device=DEVICE).manual_seed(seed)
    
    # Generate first frame
    first_frame = pipe(
        enhanced_prompt,
        height=height,
        width=width,
        num_inference_steps=20,  # Reduced steps for faster generation
        generator=generator
    ).images[0]
    
    frames.append(np.array(first_frame))
    
    # Generate subsequent frames with slight variations
    for i in range(1, num_frames):
        print(f"Generating frame {i+1}/{num_frames}")
        frame = pipe(
            enhanced_prompt,
            height=height,
            width=width,
            num_inference_steps=15,  # Fewer steps for subsequent frames
            generator=generator,
            latents=torch.randn_like(
                torch.randn((1, 4, height // 8, width // 8), 
                device=DEVICE) * 0.1 * (i / num_frames)
            )
        ).images[0]
        frames.append(np.array(frame))
    
    # Save as GIF and MP4
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Save as GIF
    gif_path = f"{output_path}.gif"
    print(f"Saving GIF to {gif_path}")
    imageio.mimsave(gif_path, frames, fps=fps, loop=0)
    
    # Save as MP4
    mp4_path = f"{output_path}.mp4"
    print(f"Saving MP4 to {mp4_path}")
    writer = imageio.get_writer(mp4_path, fps=fps, codec='libx264')
    for frame in frames:
        writer.append_data(frame)
    writer.close()
    
    total_time = time.time() - start_time
    print(f"Video generation completed in {total_time:.2f} seconds")
    
    return mp4_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate animated video from text using Text2Video-Zero")
    parser.add_argument("--prompt", type=str, required=True, 
                      help="Text prompt describing the video")
    parser.add_argument("--style", type=str, default="pixar",
                      choices=["pixar", "anime", "watercolor", "cyberpunk", "claymation"],
                      help="Animation style")
    parser.add_argument("--frames", type=int, default=8, 
                      help="Number of frames to generate (recommended: 4-16 for CPU)")
    parser.add_argument("--fps", type=int, default=4, 
                      help="Frames per second for the output video")
    parser.add_argument("--seed", type=int, default=42, 
                      help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="generated_animation", 
                      help="Output filename (without extension)")
    
    args = parser.parse_args()
    
    print(f"=== Starting Video Generation ===")
    print(f"Prompt: {args.prompt}")
    print(f"Style: {args.style}")
    print(f"Frames: {args.frames}")
    print(f"FPS: {args.fps}")
    print(f"Seed: {args.seed}")
    
    try:
        video_path = create_video_from_text(
            prompt=args.prompt,
            style=args.style,
            num_frames=args.frames,
            fps=args.fps,
            seed=args.seed,
            output_filename=args.output
        )
        
        print(f"\n=== Video Generation Completed ===")
        print(f"Output saved to: {os.path.abspath(video_path)}")
        print("You can find the video in the 'output_videos' directory.")
        
    except Exception as e:
        print(f"\n=== Error Occurred ===")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Try reducing the number of frames (--frames)")
        print("2. Try a simpler prompt")
        print("3. Check if you have enough disk space and memory")
        print("4. Make sure all dependencies are installed correctly")
        raise  # Re-raise the exception to fail the GitHub Action
