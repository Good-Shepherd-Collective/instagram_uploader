# Social Media Uploader

A comprehensive tool for posting content to Instagram and Facebook using their respective APIs.

## Project Structure

```
.
├── instagram/          # Instagram-specific functionality
│   ├── posts/         # Instagram feed posts (images & videos)
│   ├── reels/         # Instagram reels
│   └── stories/       # Instagram stories
├── facebook/          # Facebook-specific functionality (coming soon)
│   ├── posts/         # Facebook page posts
│   └── stories/       # Facebook stories
├── utils/             # Shared utilities
│   ├── token_manager.py
│   ├── get_long_lived_token.py
│   └── auto_refresh_token.py
└── .env               # Environment variables
```

## Features

### Instagram
- **Feed Posts**: Support for single images, videos, and carousel posts (up to 10 media items)
- **Reels**: Post video reels to Instagram
- **Stories**: Share temporary stories
- **Video Support**: MP4 videos are automatically posted as Reels
- **Configuration**: YAML-based configuration for posts
- **Auto-retry**: Automatic retry mechanism for video processing

### Facebook (Coming Soon)
- Page posts with images and videos
- Story functionality
- Cross-posting capabilities

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your credentials:
   ```
   ACCESS_TOKEN=your_access_token
   ACCOUNT_ID=your_instagram_business_account_id
   APP_ID=your_app_id
   APP_SECRET=your_app_secret
   CLOUDINARY_API=your_cloudinary_api_key
   CLOUDINARY_SECRET=your_cloudinary_secret
   ```

## Usage

### Instagram Posts

1. Place your media files in `instagram/posts/media/`
2. Configure your post in `instagram/posts/media/post.yaml`
3. Run: `python instagram/posts/instagram_post.py`

### Configuration Example (post.yaml)

```yaml
caption: |
  Your caption text here
  
hashtags:
  - hashtag1
  - hashtag2

alt_text: "Description for accessibility"
location: ""  # Leave empty or use Facebook location ID
user_tags:
  - username1
  - username2
```

## API References

- [Instagram API Documentation](https://developers.facebook.com/docs/instagram-api)
- [Facebook API Documentation](https://developers.facebook.com/docs/facebook-login/)

## Notes

- Videos are automatically posted as Reels (Instagram's current requirement)
- Alt text is not supported for video posts/reels
- Location requires a valid Facebook location ID
- Maximum 100 posts per 24-hour period

## Token Management

Use the utilities in the `utils/` folder to manage your access tokens:
- `get_long_lived_token.py`: Convert short-lived to long-lived tokens
- `token_manager.py`: Check token validity and refresh
- `auto_refresh_token.py`: Automatic token refresh