import requests
import os
import base64

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    caption = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Step 1: Upload image as unpublished
    with open(image_path, "rb") as img:
        upload_url = f"https://graph.facebook.com/{page_id}/photos"
        upload_response = requests.post(upload_url, data={
            "access_token": token,
            "published": "false",
            "temporary": "true"  # Don't add to any album!
        }, files={"source": img})

    upload_result = upload_response.json()
    print("Upload result:", upload_result)
    photo_id = upload_result.get("id")

    # Step 2: Post to feed as public standalone post
    feed_url = f"https://graph.facebook.com/{page_id}/feed"
    feed_response = requests.post(feed_url, data={
        "access_token": token,
        "message": caption,
        "attached_media": f'[{{"media_fbid":"{photo_id}"}}]',
    })

    result = feed_response.json()
    print("Feed post result:", result)
    return result
