import os
import requests
from dotenv import load_dotenv

load_dotenv()

def post_to_instagram():
    """Simple Instagram post"""
    access_token = os.getenv('ACCESS_TOKEN')
    account_id = os.getenv('ACCOUNT_ID')
    
    print(f"Account ID: {account_id}")
    
    # Try posting an image
    url = f"https://graph.facebook.com/v18.0/{account_id}/media"
    
    # Use a public image URL for testing
    image_url = "https://picsum.photos/1080/1080"
    
    params = {
        'image_url': image_url,
        'caption': 'Test post from API',
        'access_token': access_token
    }
    
    print("📤 Creating post...")
    response = requests.post(url, params=params)
    result = response.json()
    
    print(f"Response: {result}")
    
    if 'id' in result:
        creation_id = result['id']
        print(f"✅ Created! ID: {creation_id}")
        
        # Publish it
        publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
        publish_params = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        print("📱 Publishing...")
        pub_response = requests.post(publish_url, params=publish_params)
        pub_result = pub_response.json()
        
        print(f"Publish result: {pub_result}")
        
        if 'id' in pub_result:
            print(f"🎉 Posted! Media ID: {pub_result['id']}")
        else:
            print("❌ Publish failed")
    else:
        print("❌ Creation failed")

if __name__ == "__main__":
    post_to_instagram()