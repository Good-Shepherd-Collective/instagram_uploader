#!/usr/bin/env python3
"""
Automated token refresh script - run this daily via cron job
Add to crontab with: crontab -e
Then add: 0 9 * * * /usr/bin/python3 /path/to/utils/auto_refresh_token.py
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from utils.token_manager import TokenManager
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def send_notification(subject, body):
    """Send email notification (optional - configure if needed)"""
    # Configure these if you want email notifications
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    
    if EMAIL_FROM and EMAIL_TO and EMAIL_PASSWORD:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"📧 Notification sent to {EMAIL_TO}")
        except Exception as e:
            print(f"Failed to send email: {e}")

def main():
    print(f"\n{'='*50}")
    print(f"Token Auto-Refresh Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*50)
    
    manager = TokenManager()
    
    # Check token status
    is_valid, days_remaining = manager.check_token_status()
    
    if not is_valid:
        message = "❌ CRITICAL: Instagram token is invalid or expired!"
        print(message)
        send_notification("Instagram Token Expired", message)
        sys.exit(1)
    
    # Auto-refresh if expiring soon
    if days_remaining <= 7:
        print(f"\n⚠️ Token expiring in {days_remaining} days. Refreshing...")
        new_token = manager.refresh_token()
        
        if new_token:
            message = f"✅ Token successfully refreshed! Valid for 60 more days."
            print(message)
            send_notification("Instagram Token Refreshed", message)
        else:
            message = "❌ Failed to refresh token. Manual intervention required."
            print(message)
            send_notification("Token Refresh Failed", message)
            sys.exit(1)
    else:
        print(f"✅ Token is healthy. {days_remaining} days remaining.")
    
    print(f"\n{'='*50}\n")

if __name__ == "__main__":
    main()