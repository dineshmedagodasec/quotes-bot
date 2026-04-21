import requests
import os

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    album_id = os.getenv("FACEBOOK_ALBUM_ID")

    caption = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Step 1: Upload photo to album but unpublished
    with open(image_path, "rb") as img:
        upload_url = f"https://graph.facebook.com/{album_id}/photos"
        upload_response = requests.post(upload_url, data={
            "access_token": token,
            "published": "false"
        }, files={"source": img})

    upload_result = upload_response.json()
    photo_id = upload_result.get("id")
    print("Photo uploaded:", photo_id)

    # Step 2: Post to page feed as standalone public post
    feed_url = f"https://graph.facebook.com/{page_id}/feed"
    feed_response = requests.post(feed_url, data={
        "access_token": token,
        "message": caption,
        "attached_media": f'[{{"media_fbid":"{photo_id}"}}]',
        "published": "true"
    })

    result = feed_response.json()
    print("Feed post result:", result)
    return result
