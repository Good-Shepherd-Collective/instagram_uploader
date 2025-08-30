import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
import json

load_dotenv()

class TokenManager:
    def __init__(self):
        self.access_token = os.getenv('ACCESS_TOKEN')
        self.app_id = os.getenv('APP_ID')
        self.app_secret = os.getenv('APP_SECRET')
        self.account_id = os.getenv('ACCOUNT_ID')
        self.token_file = 'token_info.json'
    
    def check_token_status(self):
        """Check if current token is valid and when it expires"""
        url = f"https://graph.facebook.com/v18.0/debug_token"
        params = {
            'input_token': self.access_token,
            'access_token': f"{self.app_id}|{self.app_secret}"
        }
        
        print("🔍 Checking token status...")
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'data' in result:
            data = result['data']
            is_valid = data.get('is_valid', False)
            
            if is_valid:
                expires_at = data.get('expires_at', 0)
                if expires_at > 0:
                    expiry_date = datetime.fromtimestamp(expires_at)
                    days_remaining = (expiry_date - datetime.now()).days
                    
                    print(f"✅ Token is VALID")
                    print(f"📅 Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"⏰ Days remaining: {days_remaining}")
                    
                    # Save token info
                    self.save_token_info(expiry_date, days_remaining)
                    
                    # Warning if expiring soon
                    if days_remaining < 7:
                        print(f"⚠️ WARNING: Token expires in {days_remaining} days! Consider refreshing.")
                    
                    return True, days_remaining
                else:
                    print("✅ Token is valid (no expiration)")
                    return True, float('inf')
            else:
                print("❌ Token is INVALID or expired")
                error = data.get('error', {})
                if error:
                    print(f"Error: {error.get('message', 'Unknown error')}")
                return False, 0
        else:
            print(f"❌ Could not check token: {result}")
            return False, 0
    
    def refresh_token(self):
        """Refresh the long-lived token (can be done once per day, up to 60 days before expiry)"""
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': self.access_token
        }
        
        print("🔄 Refreshing long-lived token...")
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'access_token' in result:
            new_token = result['access_token']
            expires_in = result.get('expires_in', 0)
            days = expires_in // 86400
            
            print(f"✅ Token refreshed! Valid for {days} more days")
            print(f"\n📋 New token:\n{new_token}\n")
            
            # Update .env file
            set_key('.env', 'ACCESS_TOKEN', new_token)
            print("✅ Updated .env file with new token")
            
            # Update token info
            expiry_date = datetime.now() + timedelta(days=days)
            self.save_token_info(expiry_date, days)
            
            return new_token
        else:
            print(f"❌ Failed to refresh: {result}")
            return None
    
    def save_token_info(self, expiry_date, days_remaining):
        """Save token information to a JSON file"""
        info = {
            'last_checked': datetime.now().isoformat(),
            'expires_at': expiry_date.isoformat(),
            'days_remaining': days_remaining,
            'account_id': self.account_id
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(info, f, indent=2)
    
    def load_token_info(self):
        """Load saved token information"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                info = json.load(f)
                
            print("\n📊 Saved Token Info:")
            print(f"Last checked: {info['last_checked']}")
            print(f"Expires at: {info['expires_at']}")
            print(f"Days remaining (at last check): {info['days_remaining']}")
            return info
        else:
            print("No saved token info found")
            return None
    
    def auto_refresh_if_needed(self):
        """Automatically refresh token if it's expiring soon"""
        is_valid, days_remaining = self.check_token_status()
        
        if is_valid and days_remaining < 7:
            print(f"\n🔄 Auto-refreshing token (expires in {days_remaining} days)...")
            return self.refresh_token()
        elif not is_valid:
            print("\n❌ Token is invalid. Please get a new token from Graph API Explorer.")
            return None
        else:
            print(f"\n✅ Token is healthy ({days_remaining} days remaining)")
            return self.access_token

if __name__ == "__main__":
    manager = TokenManager()
    # Directly check token status
    manager.check_token_status()