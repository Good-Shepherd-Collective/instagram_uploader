import os
import sys
import re
import glob
import yaml
import requests
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# Configure Cloudinary
cloudinary.config(
    cloud_name="dyemob08j",
    api_key=os.getenv('CLOUDINARY_API'),
    api_secret=os.getenv('CLOUDINARY_SECRET')
)

def parse_post_config(yaml_file_path):
    """Parse the post.yaml file to extract configuration"""
    config = {
        'caption': '',
        'hashtags': '',
        'alt_text': '',
        'location': '',
        'user_tags': [],
        'product_tags': [],
        'branded_content_partner': '',
        'disable_comments': False,
        'hide_like_count': False,
        'collaborators': [],
        'scheduled_publish_time': '',
        'notes': ''
    }
    
    # Try YAML file first
    if not os.path.exists(yaml_file_path):
        # Fall back to markdown file for backward compatibility
        md_file_path = yaml_file_path.replace('.yaml', '.md')
        if os.path.exists(md_file_path):
            print(f"⚠️ Found legacy post.md file. Please migrate to post.yaml format.")
            return parse_legacy_markdown(md_file_path)
        else:
            print(f"⚠️ No post.yaml found at {yaml_file_path}, using defaults")
            return config
    
    with open(yaml_file_path, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML file: {e}")
            return config
    
    # Map YAML data to config
    if data:
        config['caption'] = data.get('caption', '').strip()
        
        # Handle hashtags (can be list or string)
        hashtags = data.get('hashtags', [])
        if isinstance(hashtags, list):
            config['hashtags'] = ' '.join([f"#{tag}" if not tag.startswith('#') else tag for tag in hashtags])
        elif isinstance(hashtags, str):
            config['hashtags'] = hashtags
        
        config['alt_text'] = data.get('alt_text', '')
        config['location'] = data.get('location', '')
        
        # Handle user tags (remove @ if present)
        user_tags = data.get('user_tags', [])
        if isinstance(user_tags, list):
            config['user_tags'] = [tag.lstrip('@') for tag in user_tags if tag]
        
        config['product_tags'] = data.get('product_tags', [])
        config['branded_content_partner'] = data.get('branded_content_partner', '')
        config['disable_comments'] = data.get('disable_comments', False)
        config['hide_like_count'] = data.get('hide_like_count', False)
        config['collaborators'] = data.get('collaborators', [])
        config['scheduled_publish_time'] = data.get('scheduled_publish_time', '')
        config['notes'] = data.get('notes', '')
    
    # Combine caption and hashtags
    if config['hashtags']:
        config['full_caption'] = f"{config['caption']}\n\n{config['hashtags']}"
    else:
        config['full_caption'] = config['caption']
    
    return config

def parse_legacy_markdown(md_file_path):
    """Parse legacy post.md file for backward compatibility"""
    config = {
        'caption': '',
        'hashtags': '',
        'alt_text': '',
        'location': '',
        'user_tags': [],
        'product_tags': [],
        'branded_content_partner': '',
        'disable_comments': False,
        'hide_like_count': False,
        'full_caption': ''
    }
    
    with open(md_file_path, 'r') as f:
        content = f.read()
    
    # Extract sections using regex
    sections = {
        'Caption': 'caption',
        'Hashtags': 'hashtags',
        'Alt Text': 'alt_text',
        'Location': 'location',
        'User Tags': 'user_tags',
        'Product Tags': 'product_tags',
        'Branded Content': 'branded_content_partner',
        'Comments Disabled': 'disable_comments',
        'Hide Like Count': 'hide_like_count'
    }
    
    for section, key in sections.items():
        pattern = rf'## {section}\n(.*?)(?=\n##|\n\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            value = match.group(1).strip()
            
            if key == 'user_tags':
                config[key] = re.findall(r'@(\w+)', value)
            elif key == 'product_tags':
                config[key] = [pid.strip() for pid in value.split(',') if pid.strip()]
            elif key in ['disable_comments', 'hide_like_count']:
                config[key] = value.lower() == 'true'
            else:
                config[key] = value
    
    if config['hashtags']:
        config['full_caption'] = f"{config['caption']}\n\n{config['hashtags']}"
    else:
        config['full_caption'] = config['caption']
    
    return config

def get_media_files(media_folder):
    """Get all media files (images and videos) from the media folder"""
    supported_formats = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG', '*.mp4', '*.MP4']
    media_files = []
    
    for format in supported_formats:
        pattern = os.path.join(media_folder, format)
        media_files.extend(glob.glob(pattern))
    
    # Sort files for consistent ordering
    media_files.sort()
    return media_files

def upload_to_cloudinary(file_path):
    """Upload a single file to Cloudinary"""
    try:
        print(f"  ☁️ Uploading: {os.path.basename(file_path)}")
        # Check if it's a video file
        if file_path.lower().endswith(('.mp4')):
            upload_result = cloudinary.uploader.upload(file_path, resource_type="video")
        else:
            upload_result = cloudinary.uploader.upload(file_path)
        return upload_result['secure_url']
    except Exception as e:
        print(f"  ❌ Failed to upload {file_path}: {e}")
        return None

def create_carousel_post(media_items, config):
    """Create a carousel post with multiple images/videos"""
    access_token = os.getenv('ACCESS_TOKEN')
    account_id = os.getenv('ACCOUNT_ID')
    
    media_ids = []
    
    # Create media objects for each media item
    for i, (media_url, media_type) in enumerate(media_items):
        print(f"\n📸 Creating media {i+1}/{len(media_items)}...")
        
        url = f"https://graph.facebook.com/v18.0/{account_id}/media"
        params = {
            'is_carousel_item': 'true',
            'access_token': access_token
        }
        
        # Use appropriate parameter based on media type
        if media_type == 'video':
            params['video_url'] = media_url
            params['media_type'] = 'REELS'
        else:
            params['image_url'] = media_url
        
        response = requests.post(url, params=params)
        result = response.json()
        
        if 'id' in result:
            media_ids.append(result['id'])
            print(f"  ✅ Media created: {result['id']}")
        else:
            print(f"  ❌ Failed to create media: {result}")
            return None
    
    # Create the carousel container
    print("\n🎠 Creating carousel container...")
    container_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
    container_params = {
        'caption': config['full_caption'],
        'media_type': 'CAROUSEL',
        'children': ','.join(media_ids),
        'access_token': access_token
    }
    
    # Add optional parameters
    if config['location']:
        container_params['location_id'] = config['location']
    if config['user_tags']:
        container_params['user_tags'] = ','.join(config['user_tags'])
    
    response = requests.post(container_url, params=container_params)
    result = response.json()
    
    if 'id' in result:
        return result['id']
    else:
        print(f"❌ Failed to create carousel: {result}")
        return None

def create_single_post(media_url, media_type, config):
    """Create a single image or video post"""
    access_token = os.getenv('ACCESS_TOKEN')
    account_id = os.getenv('ACCOUNT_ID')
    
    print(f"📸 Creating single {'video' if media_type == 'video' else 'image'} post...")
    
    url = f"https://graph.facebook.com/v18.0/{account_id}/media"
    params = {
        'caption': config['full_caption'],
        'access_token': access_token
    }
    
    # Use appropriate parameter based on media type
    if media_type == 'video':
        params['video_url'] = media_url
        params['media_type'] = 'REELS'
    else:
        params['image_url'] = media_url
    
    # Add optional parameters (alt_text not supported for REELS)
    if config['alt_text'] and media_type != 'video':
        params['alt_text'] = config['alt_text']
    if config['location']:
        params['location_id'] = config['location']
    if config['user_tags']:
        params['user_tags'] = ','.join(config['user_tags'])
    
    response = requests.post(url, params=params)
    result = response.json()
    
    if 'id' in result:
        return result['id']
    else:
        print(f"❌ Failed to create post: {result}")
        return None

def publish_post(creation_id, config):
    """Publish the created media"""
    import time
    access_token = os.getenv('ACCESS_TOKEN')
    account_id = os.getenv('ACCOUNT_ID')
    
    print("\n📤 Publishing post...")
    
    publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
    publish_params = {
        'creation_id': creation_id,
        'access_token': access_token
    }
    
    # Retry mechanism for video processing
    max_retries = 5
    retry_delay = 10  # seconds
    
    for attempt in range(max_retries):
        response = requests.post(publish_url, params=publish_params)
        result = response.json()
        
        if 'id' in result:
            print(f"🎉 SUCCESS! Posted to Instagram!")
            print(f"📱 Media ID: {result['id']}")
            return result['id']
        elif 'error' in result and result['error'].get('code') == 9007:
            # Media still processing
            if attempt < max_retries - 1:
                print(f"⏳ Media still processing... waiting {retry_delay} seconds (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            else:
                print(f"❌ Media took too long to process after {max_retries} attempts")
                break
        else:
            print(f"❌ Publish failed: {result}")
            break
    
    return None

def main():
    """Main function to post all images in media folder"""
    media_folder = os.path.join(os.path.dirname(__file__), 'media')
    yaml_file = os.path.join(media_folder, 'post.yaml')
    
    print("=== Instagram Multi-Image Poster ===\n")
    
    # Parse configuration
    print("📋 Reading post configuration...")
    config = parse_post_config(yaml_file)
    print(f"  Caption: {config['caption'][:50]}..." if len(config['caption']) > 50 else f"  Caption: {config['caption']}")
    print(f"  Hashtags: {config['hashtags']}")
    
    # Show additional metadata if present
    if config['location']:
        print(f"  📍 Location: {config['location']}")
    if config['user_tags']:
        print(f"  👥 User tags: {', '.join(config['user_tags'])}")
    if config['scheduled_publish_time']:
        print(f"  ⏰ Scheduled: {config['scheduled_publish_time']}")
    
    # Get media files
    media_files = get_media_files(media_folder)
    
    if not media_files:
        print(f"\n❌ No images found in {media_folder}")
        print("Please add JPG or PNG images to the media folder.")
        return
    
    print(f"\n📁 Found {len(media_files)} media file(s):")
    for file in media_files:
        print(f"  - {os.path.basename(file)}")
    
    # Upload all media files to Cloudinary and track their types
    print("\n☁️ Uploading to Cloudinary...")
    media_items = []
    for file in media_files:
        url = upload_to_cloudinary(file)
        if url:
            # Determine media type based on file extension
            media_type = 'video' if file.lower().endswith('.mp4') else 'image'
            media_items.append((url, media_type))
    
    if not media_items:
        print("\n❌ No media files were successfully uploaded")
        return
    
    # Create Instagram post
    if len(media_items) > 1:
        # Create carousel post
        print(f"\n🎠 Creating carousel with {len(media_items)} media items...")
        creation_id = create_carousel_post(media_items, config)
    else:
        # Create single post
        media_url, media_type = media_items[0]
        print(f"\n📷 Creating single {'video' if media_type == 'video' else 'image'} post...")
        creation_id = create_single_post(media_url, media_type, config)
    
    # Publish the post
    if creation_id:
        publish_post(creation_id, config)
    else:
        print("\n❌ Failed to create Instagram post")

if __name__ == "__main__":
    main()