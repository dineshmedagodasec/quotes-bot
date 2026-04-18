import requests
import os
from dotenv import load_dotenv

load_dotenv()

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    caption = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Step 1: Upload image unpublished first
    with open(image_path, "rb") as img:
        upload_url = f"https://graph.facebook.com/{page_id}/photos"
        upload_response = requests.post(upload_url, data={
            "access_token": token,
            "published": "false"  # upload but don't post yet
        }, files={"source": img})

    upload_result = upload_response.json()
    print("Upload result:", upload_result)
    photo_id = upload_result.get("id")

    # Step 2: Publish as a proper public post
    post_url = f"https://graph.facebook.com/{page_id}/feed"
    post_response = requests.post(post_url, data={
        "access_token": token,
        "message": caption,
        "attached_media": f'[{{"media_fbid":"{photo_id}"}}]',
        "privacy": '{"value":"EVERYONE"}',  # force public
    })

    result = post_response.json()
    print("Post result:", result)
    return result