import requests
import os
import base64

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    caption = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Post directly to page photos - simplest method
    with open(image_path, "rb") as img:
        response = requests.post(
            f"https://graph.facebook.com/{page_id}/photos",
            data={
                "caption": caption,
                "access_token": token,
                "published": "true",
                "no_story": "false",
                "place": "",
                "targeting": '{"geo_locations":{"countries":["US","GB","LK","AU","CA"]}}' 
            },
            files={"source": img}
        )

    result = response.json()
    print("Posted successfully:", result)
    return result
