import os
import subprocess
from instagram_reels import InstagramReels
from dotenv import load_dotenv

load_dotenv()

def image_to_video(image_path, output_path, duration=5):
    """
    Convert an image to a video for Instagram Reels
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path for the output video
        duration (int): Duration in seconds
    """
    try:
        # Use ffmpeg to convert image to video
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
            '-loop', '1',    # Loop the input
            '-i', image_path,  # Input image
            '-c:v', 'libx264',  # Video codec
            '-t', str(duration),  # Duration
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-vf', 'scale=1080:1920',  # Instagram Reels aspect ratio (9:16)
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Video created: {output_path}")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ FFmpeg not found. Install with: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def post_image_as_reel(image_path, caption="", duration=5):
    """
    Convert image to video and post as Reel
    
    Args:
        image_path (str): Path to the image file
        caption (str): Caption for the reel
        duration (int): Video duration in seconds
    """
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
        
    # Create output video path
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    video_path = f"{base_name}_reel.mp4"
    
    print(f"🎬 Converting image to video...")
    if image_to_video(image_path, video_path, duration):
        print(f"📱 Posting to Instagram Reels...")
        
        reels = InstagramReels()
        result = reels.post_reel(video_path, caption)
        
        if result.get('success'):
            print(f"🎉 Reel posted successfully! Media ID: {result['media_id']}")
            # Clean up video file
            os.remove(video_path)
            print(f"🗑️ Cleaned up temporary video file")
        else:
            print(f"❌ Failed to post: {result.get('error', 'Unknown error')}")
    else:
        print("❌ Failed to create video from image")

if __name__ == "__main__":
    image_file = "Generated Image August 29, 2025 - 6_43PM.jpeg"
    caption = "AI Generated Image - August 29, 2025"
    
    post_image_as_reel(image_file, caption, duration=10)