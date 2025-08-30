import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_long_lived_token():
    """Exchange short-lived token for long-lived token (60 days)"""
    
    # Your current short-lived access token
    short_lived_token = os.getenv('ACCESS_TOKEN')
    
    # Get your Instagram App Secret from Facebook Developer Console
    client_secret = os.getenv('APP_SECRET')  # You need to add this to .env
    
    if not client_secret:
        print("❌ Please add APP_SECRET to your .env file")
        print("You can find it in Facebook Developer Console:")
        print("1. Go to https://developers.facebook.com/apps")
        print("2. Select your app")
        print("3. Settings > Basic > App Secret")
        return
    
    # Exchange for long-lived token
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': os.getenv('APP_ID'),  # Your Instagram App ID
        'client_secret': client_secret,
        'fb_exchange_token': short_lived_token
    }
    
    print("🔄 Exchanging for long-lived token...")
    response = requests.get(url, params=params)
    result = response.json()
    
    if 'access_token' in result:
        long_lived_token = result['access_token']
        expires_in = result.get('expires_in', 0)
        days = expires_in // 86400  # Convert seconds to days
        
        print(f"✅ Success! Token expires in {days} days")
        print(f"\n📋 Your long-lived token:\n{long_lived_token}\n")
        print("📝 Update your .env file with:")
        print(f"ACCESS_TOKEN={long_lived_token}")
        
        # Optional: Save to a new file
        with open('long_lived_token.txt', 'w') as f:
            f.write(f"Token: {long_lived_token}\n")
            f.write(f"Expires in: {days} days\n")
        print("\n💾 Token also saved to long_lived_token.txt")
        
        return long_lived_token
    else:
        print(f"❌ Failed to get long-lived token: {result}")
        return None

def refresh_long_lived_token():
    """Refresh a long-lived token before it expires"""
    
    current_token = os.getenv('ACCESS_TOKEN')
    
    url = f"https://graph.facebook.com/v18.0/refresh_access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'fb_exchange_token': current_token
    }
    
    print("🔄 Refreshing long-lived token...")
    response = requests.get(url, params=params)
    result = response.json()
    
    if 'access_token' in result:
        new_token = result['access_token']
        print(f"✅ Token refreshed successfully!")
        print(f"\n📋 Your refreshed token:\n{new_token}\n")
        return new_token
    else:
        print(f"❌ Failed to refresh token: {result}")
        return None

if __name__ == "__main__":
    print("=== Instagram Long-Lived Token Generator ===")
    # Directly exchange for long-lived token
    get_long_lived_token()