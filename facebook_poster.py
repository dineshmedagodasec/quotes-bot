import requests
import os

def post_to_facebook(video_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    description = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Post video directly to page
    video_url = f"https://graph-video.facebook.com/{page_id}/videos"
    
    with open(video_path, "rb") as video_file:
        response = requests.post(video_url, data={
            "access_token": token,
            "description": description,
            "published": "true"
        }, files={"source": video_file})

    result = response.json()
    print("Posted video:", result)
    return result
