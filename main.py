import os
import datetime
import random
from dotenv import load_dotenv
from quote_fetcher import get_quote
from image_maker import create_quote_image
from facebook_poster import post_to_facebook
from youtube_video_maker import create_youtube_short
from youtube_poster import post_to_youtube
from question_poster import create_question_video
from viral_short_maker import create_viral_short
from countdown_short_maker import create_countdown_video

load_dotenv()

def get_post_type():
    utc_hour = datetime.datetime.utcnow().hour
    if utc_hour in [15, 20]:
        return "question"
    elif utc_hour == 1:
        return "countdown"
    elif utc_hour == 22:
        return "viral"
    else:
        return "quote"

def run_bot():
    post_type = get_post_type()
    print(f"Post type: {post_type}")

    if post_type == "question":
        print("Question post time!")
        quote, author, hook = create_question_video()
        fb_image_path, yt_image_path = create_quote_image(quote, author)
        video_path = create_youtube_short(quote, author, yt_image_path)

    elif post_type == "countdown":
        print("Countdown video time!")
        video_path, quote, author = create_countdown_video()
        fb_image_path, yt_image_path = create_quote_image(quote, author)

    elif post_type == "viral":
        print("Viral short time!")
        quote, author, cta = create_viral_short()
        fb_image_path, yt_image_path = create_quote_image(quote, author)
        video_path = create_youtube_short(quote, author, yt_image_path)

    else:
        print("Regular quote time!")
        quote, author = get_quote()
        fb_image_path, yt_image_path = create_quote_image(quote, author)
        video_path = create_youtube_short(quote, author, yt_image_path)

    print(f"Quote: {quote[:50]}")

    print("Posting to Facebook...")
    fb_result = post_to_facebook(
        fb_image_path,
        quote,
        author,
        video_path=video_path
    )
    print(f"Facebook done: {fb_result}")

    print("Uploading to YouTube...")
    yt_result = post_to_youtube(video_path, quote, author)
    print(f"YouTube done: {yt_result}")

if __name__ == "__main__":
    run_bot()
