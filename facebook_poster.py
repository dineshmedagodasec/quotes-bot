import requests
import os
from dotenv import load_dotenv

load_dotenv()

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    caption = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Upload image and post
    with open(image_path, "rb") as img:
        upload_url = f"https://graph.facebook.com/{page_id}/photos"
        response = requests.post(upload_url, data={
            "caption": caption,
            "access_token": token,
            "published": "true"
        }, files={"source": img})

    result = response.json()
    print("Response:", result)
    return result