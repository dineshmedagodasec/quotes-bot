import requests
import os

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    album_id = os.getenv("FACEBOOK_ALBUM_ID")  # Public album ID

    caption = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Post directly into the public album
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
