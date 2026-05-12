import requests
import os
import random

QUESTIONS = [
    "Tag someone who needs to hear this today!",
    "Does this quote speak to you? Comment YES!",
    "What does this quote mean to you?",
    "Share this with someone who needs motivation!",
    "Type YES if you needed to hear this today!",
    "Who in your life needs to see this?",
    "Comment your favorite motivational quote below!",
    "Does this describe your life right now?",
    "What is your biggest takeaway from this?",
    "Which part resonates with you most?",
]

def format_caption(quote, author):
    question = random.choice(QUESTIONS)
    lines = quote.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            formatted_lines.append(line)
        else:
            formatted_lines.append('')
    formatted_quote = '\n'.join(formatted_lines)

    caption = f'"{formatted_quote}"\n\n— {author}\n\n💬 {question}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes #DailyMotivation #InspirationalQuotes #MotivationalQuotes'

    return caption

def post_to_facebook(image_path, quote, author, video_path=None):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    album_id = os.getenv("FACEBOOK_ALBUM_ID")

    caption = format_caption(quote, author)

    # Try posting as Reel first if video exists
    if video_path and os.path.exists(video_path):
        print("Posting as Facebook Reel...")
        reel_result = post_as_reel(page_id, token, video_path, caption)
        if reel_result:
            return reel_result

    # Fallback to photo post
    print("Posting as photo...")
    with open(image_path, "rb") as img:
        upload_url = f"https://graph.facebook.com/{album_id}/photos"
        response = requests.post(upload_url, data={
            "caption": caption,
            "access_token": token,
            "published": "true"
        }, files={"source": img})

    result = response.json()
    print("Posted successfully:", result)
    return result

def post_as_reel(page_id, token, video_path, caption):
    try:
        # Step 1: Initialize reel upload
        init_url = f"https://graph.facebook.com/{page_id}/video_reels"
        video_size = os.path.getsize(video_path)

        init_response = requests.post(init_url, data={
            "access_token": token,
            "upload_phase": "start",
            "video_file_size": video_size
        })
        init_result = init_response.json()
        print(f"Reel init: {init_result}")

        video_id = init_result.get("video_id")
        upload_url = init_result.get("upload_url")

        if not video_id or not upload_url:
            print("Reel init failed — falling back to photo")
            return None

        # Step 2: Upload video
        with open(video_path, "rb") as video_file:
            video_data = video_file.read()

        upload_response = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {token}",
                "offset": "0",
                "file_size": str(video_size)
            },
            data=video_data
        )
        print(f"Reel upload: {upload_response.status_code}")

        # Step 3: Publish reel
        publish_url = f"https://graph.facebook.com/{page_id}/video_reels"
        publish_response = requests.post(publish_url, data={
            "access_token": token,
            "video_id": video_id,
            "upload_phase": "finish",
            "video_state": "PUBLISHED",
            "description": caption,
            "title": caption[:100]
        })

        result = publish_response.json()
        print(f"Reel published: {result}")

        if "error" not in result:
            print("Facebook Reel posted successfully!")
            return result
        else:
            print(f"Reel publish failed: {result}")
            return None

    except Exception as e:
        print(f"Reel posting failed: {e}")
        return None
