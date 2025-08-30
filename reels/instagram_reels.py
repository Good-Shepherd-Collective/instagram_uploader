import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class InstagramReels:
    def __init__(self):
        self.access_token = os.getenv('ACCESS_TOKEN') or os.getenv('GSC_ACCESS_TOKEN')
        self.account_id = os.getenv('ACCOUNT_ID')
        
    def upload_video(self, video_url, caption="", cover_url=None, share_to_feed=True):
        """
        Upload a video to Instagram Reels
        
        Args:
            video_url (str): URL of the video file
            caption (str): Caption for the reel
            cover_url (str): URL of the cover image (optional)
            share_to_feed (bool): Whether to share to main feed
            
        Returns:
            dict: Response containing creation_id or error
        """
        url = f"https://graph.facebook.com/v18.0/{self.account_id}/media"
        
        params = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'share_to_feed': share_to_feed,
            'access_token': self.access_token
        }
        
        if cover_url:
            params['cover_url'] = cover_url
            
        try:
            response = requests.post(url, params=params)
            return response.json()
        except Exception as e:
            return {'error': f'Upload failed: {str(e)}'}
    
    def upload_local_video(self, video_path, caption="", share_to_feed=True):
        """
        Upload a local video file to Instagram Reels using resumable upload
        
        Args:
            video_path (str): Path to local video file
            caption (str): Caption for the reel
            share_to_feed (bool): Whether to share to main feed
            
        Returns:
            dict: Response containing creation_id or error
        """
        if not os.path.exists(video_path):
            return {'error': f'Video file not found: {video_path}'}
        
        # Step 1: Initialize upload session
        init_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media"
        
        file_size = os.path.getsize(video_path)
        
        init_data = {
            'media_type': 'REELS',
            'caption': caption,
            'share_to_feed': share_to_feed,
            'file_size': file_size,
            'access_token': self.access_token
        }
        
        try:
            # Initialize upload
            init_response = requests.post(init_url, data=init_data)
            init_result = init_response.json()
            
            if 'error' in init_result:
                return init_result
                
            if 'id' not in init_result:
                return {'error': 'No upload session ID returned'}
                
            upload_id = init_result['id']
            
            # Step 2: Upload the video file
            upload_url = f"https://graph.facebook.com/v18.0/{upload_id}"
            
            with open(video_path, 'rb') as video_file:
                files = {'source': video_file}
                upload_response = requests.post(upload_url, files=files, data={'access_token': self.access_token})
                
            return upload_response.json()
            
        except Exception as e:
            return {'error': f'Upload failed: {str(e)}'}
    
    def publish_media(self, creation_id):
        """
        Publish the uploaded media
        
        Args:
            creation_id (str): The creation_id from upload response
            
        Returns:
            dict: Response containing media_id or error
        """
        url = f"https://graph.facebook.com/v18.0/{self.account_id}/media_publish"
        
        params = {
            'creation_id': creation_id,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, params=params)
            return response.json()
        except Exception as e:
            return {'error': f'Publish failed: {str(e)}'}
    
    def check_upload_status(self, creation_id):
        """
        Check the status of an uploaded media
        
        Args:
            creation_id (str): The creation_id from upload response
            
        Returns:
            dict: Status information
        """
        url = f"https://graph.facebook.com/v18.0/{creation_id}"
        
        params = {
            'fields': 'status_code,status',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            return {'error': f'Status check failed: {str(e)}'}
    
    def post_reel(self, video_path_or_url, caption="", wait_for_processing=True, max_wait_time=300):
        """
        Complete workflow to post a reel
        
        Args:
            video_path_or_url (str): Local file path or URL to video
            caption (str): Caption for the reel
            wait_for_processing (bool): Whether to wait for video processing
            max_wait_time (int): Maximum time to wait for processing (seconds)
            
        Returns:
            dict: Final result with media_id or error
        """
        print(f"🎬 Starting Reel upload...")
        
        # Upload video
        if video_path_or_url.startswith(('http://', 'https://')):
            upload_result = self.upload_video(video_path_or_url, caption)
        else:
            upload_result = self.upload_local_video(video_path_or_url, caption)
        
        if 'error' in upload_result:
            print(f"❌ Upload failed: {upload_result['error']}")
            return upload_result
            
        if 'id' not in upload_result:
            print(f"❌ Upload failed: {upload_result}")
            return {'error': 'No creation_id in response'}
            
        creation_id = upload_result['id']
        print(f"✅ Video uploaded! Creation ID: {creation_id}")
        
        # Wait for processing if requested
        if wait_for_processing:
            print("⏳ Waiting for video processing...")
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status = self.check_upload_status(creation_id)
                
                if 'error' in status:
                    print(f"❌ Status check failed: {status['error']}")
                    break
                    
                status_code = status.get('status_code')
                print(f"📊 Status: {status.get('status', 'Unknown')} (Code: {status_code})")
                
                if status_code == 'FINISHED':
                    break
                elif status_code == 'ERROR':
                    return {'error': 'Video processing failed'}
                    
                time.sleep(10)  # Wait 10 seconds before checking again
        
        # Publish the media
        print("📤 Publishing Reel...")
        publish_result = self.publish_media(creation_id)
        
        if 'error' in publish_result:
            print(f"❌ Publish failed: {publish_result['error']}")
            return publish_result
            
        if 'id' in publish_result:
            media_id = publish_result['id']
            print(f"🎉 Reel posted successfully! Media ID: {media_id}")
            return {'success': True, 'media_id': media_id, 'creation_id': creation_id}
        else:
            print(f"❌ Publish failed: {publish_result}")
            return {'error': 'Failed to get media_id from publish response'}

def main():
    """Example usage"""
    reels = InstagramReels()
    
    # Test with a sample video URL or local file
    video_path = input("Enter video file path or URL: ").strip()
    caption = input("Enter caption (optional): ").strip()
    
    if not video_path:
        print("❌ No video path provided")
        return
        
    result = reels.post_reel(video_path, caption)
    
    if result.get('success'):
        print(f"✅ Success! Your Reel is live: Media ID {result['media_id']}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()