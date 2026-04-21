import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def post_to_youtube(video_path, quote, author):
    creds = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )

    youtube = build("youtube", "v3", credentials=creds)

    # Fix title - make sure it's never empty and within 100 char limit
    raw_title = f"{quote[:70]} — {author[:20]}"
    title = raw_title.strip()
    if not title:
        title = "Daily Motivational Quote"

    description = f'"{quote}"\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Shorts #Motivation #Quotes #DailyQuote #Inspiration'

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["motivation", "quotes", "shorts", "inspiration", "dailyquote"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    response = request.execute()
    print("YouTube Short uploaded:", response)
    return response
