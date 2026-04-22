import os
from dotenv import load_dotenv
from quote_fetcher import get_quote
from image_maker import create_quote_image
from facebook_poster import post_to_facebook
from youtube_video_maker import create_youtube_short
from youtube_poster import post_to_youtube

load_dotenv()

def run_bot():
    print("🔄 Fetching quote...")
    quote, author = get_quote()
    print(f"✅ Quote: {quote} — {author}")

    print("🎨 Creating images...")
    fb_image_path, yt_image_path = create_quote_image(quote, author)
    print(f"✅ Facebook image: {fb_image_path}")
    print(f"✅ YouTube image: {yt_image_path}")

    print("📤 Posting to Facebook...")
    fb_result = post_to_facebook(fb_image_path, quote, author)
    print(f"✅ Facebook done: {fb_result}")

    print("🎬 Creating YouTube Short...")
    video_path = create_youtube_short(quote, author, yt_image_path)
    print(f"✅ Video created: {video_path}")

    print("📤 Uploading to YouTube...")
    yt_result = post_to_youtube(video_path, quote, author)
    print(f"✅ YouTube done: {yt_result}")

if __name__ == "__main__":
    run_bot()
