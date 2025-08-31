import os
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# Configure Cloudinary
cloudinary.config(
    cloud_name="dyemob08j",
    api_key=os.getenv('CLOUDINARY_API'),
    api_secret=os.getenv('CLOUDINARY_SECRET')
)

def upload_and_post_story(image_path):
    """Upload image to Cloudinary and post to Instagram Stories"""
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Step 1: Upload to Cloudinary
    print(f"☁️ Uploading to Cloudinary: {image_path}")
    try:
        upload_result = cloudinary.uploader.upload(image_path)
        image_url = upload_result['secure_url']
        print(f"✅ Uploaded! URL: {image_url}")
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return
    
    # Step 2: Post to Instagram Stories
    access_token = os.getenv('ACCESS_TOKEN')
    account_id = os.getenv('ACCOUNT_ID')
    
    print(f"Account ID: {account_id}")
    
    # Create media object for stories
    url = f"https://graph.facebook.com/v18.0/{account_id}/media"
    
    params = {
        'image_url': image_url,
        'media_type': 'STORIES',
        'access_token': access_token
    }
    
    print("📤 Creating story...")
    response = requests.post(url, params=params)
    result = response.json()
    
    print(f"Response: {result}")
    
    if 'id' in result:
        creation_id = result['id']
        print(f"✅ Created! ID: {creation_id}")
        
        # Publish the story
        publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
        publish_params = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        print("📱 Publishing story...")
        pub_response = requests.post(publish_url, params=publish_params)
        pub_result = pub_response.json()
        
        print(f"Publish result: {pub_result}")
        
        if 'id' in pub_result:
            print(f"🎉 Story posted! Media ID: {pub_result['id']}")
            print(f"🔗 Image hosted at: {image_url}")
            return pub_result['id']
        else:
            print(f"❌ Publish failed: {pub_result}")
            return None
    else:
        print(f"❌ Creation failed: {result}")
        return None

def post_video_to_stories():
    """Post video to Instagram Stories"""
    access_token = os.getenv('ACCESS_TOKEN')
    account_id = os.getenv('ACCOUNT_ID')
    
    print(f"Account ID: {account_id}")
    
    # Create media object for video stories
    url = f"https://graph.facebook.com/v18.0/{account_id}/media"
    
    # Use a public video URL for testing (must be MP4, max 15 seconds for stories)
    video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
    
    params = {
        'video_url': video_url,
        'media_type': 'STORIES',
        'access_token': access_token
    }
    
    print("📤 Creating video story...")
    response = requests.post(url, params=params)
    result = response.json()
    
    print(f"Response: {result}")
    
    if 'id' in result:
        creation_id = result['id']
        print(f"✅ Created! ID: {creation_id}")
        
        # Check status (videos need processing)
        status_url = f"https://graph.facebook.com/v18.0/{creation_id}"
        status_params = {
            'fields': 'status_code',
            'access_token': access_token
        }
        
        import time
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            print(f"⏳ Checking status (attempt {attempt + 1}/{max_attempts})...")
            status_response = requests.get(status_url, params=status_params)
            status_result = status_response.json()
            
            if 'status_code' in status_result:
                if status_result['status_code'] == 'FINISHED':
                    print("✅ Video processing complete!")
                    break
                elif status_result['status_code'] == 'ERROR':
                    print(f"❌ Video processing error: {status_result}")
                    return None
            
            time.sleep(2)
            attempt += 1
        
        # Publish the story
        publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
        publish_params = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        print("📱 Publishing video story...")
        pub_response = requests.post(publish_url, params=publish_params)
        pub_result = pub_response.json()
        
        print(f"Publish result: {pub_result}")
        
        if 'id' in pub_result:
            print(f"🎉 Video story posted! Media ID: {pub_result['id']}")
            return pub_result['id']
        else:
            print(f"❌ Publish failed: {pub_result}")
            return None
    else:
        print(f"❌ Creation failed: {result}")
        return None

if __name__ == "__main__":
    # Post the specified image to Instagram Stories
    image_file = "Arafat_Jasser_Ahmad_Amer.jpg"
    upload_and_post_story(image_file)