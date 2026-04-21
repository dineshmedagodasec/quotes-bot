import requests
import os

def post_to_facebook(video_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    description = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    # Step 1: Initialize the upload
    init_url = f"https://graph.facebook.com/{page_id}/video_reels"
    init_response = requests.post(init_url, data={
        "access_token": token,
        "upload_phase": "start",
        "video_file_size": os.path.getsize(video_path)
    })
    init_result = init_response.json()
    print("Init result:", init_result)

    video_id = init_result.get("video_id")
    upload_url = init_result.get("upload_url")

    # Step 2: Upload the video
    with open(video_path, "rb") as video_file:
        video_data = video_file.read()

    upload_response = requests.post(
        upload_url,
        headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(os.path.getsize(video_path))
        },
        data=video_data
    )
    print("Upload result:", upload_response.json())

    # Step 3: Publish the reel
    publish_url = f"https://graph.facebook.com/{page_id}/video_reels"
    publish_response = requests.post(publish_url, data={
        "access_token": token,
        "video_id": video_id,
        "upload_phase": "finish",
        "video_state": "PUBLISHED",
        "description": description,
        "title": f"{quote[:60]}..."
    })

    result = publish_response.json()
    print("Published reel:", result)
    return result
