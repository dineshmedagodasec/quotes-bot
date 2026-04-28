import os
import random
import datetime
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from thumbnail_maker import create_thumbnail

TITLE_TEMPLATES = [
    "This Will Change Your Life 🔥 #{author}",
    "Words That Will Give You Chills ✨ #{author}",
    "Morning Motivation That Hits Different 💯",
    "This Quote Changed Everything 🙏 #{author}",
    "Listen To This Every Morning 💪",
    "The Most Powerful Quote You'll Hear Today 🌟",
    "This Hit Me Hard 😮 #{author}",
    "Words Of Wisdom That Will Inspire You ✨",
    "Start Your Day With This 🌅 #{author}",
    "This Is The Motivation You Need Today 🔥",
    "One Quote That Will Change Your Mindset 💡",
    "The Truth About Success 💯 #{author}",
    "This Quote Will Stay With You Forever 🙏",
    "Powerful Words For A Powerful Life 💪",
    "When You Need Motivation Watch This 🌟",
]

TAGS = [
    "motivation", "shorts", "quotes", "dailymotivation",
    "inspirationalquotes", "motivationalquotes", "mindset",
    "success", "inspire", "lifequotes", "viral", "positivevibes",
    "selfimprovement", "growthmindset", "dailyquotes",
    "motivationalspeech", "successquotes", "wisdomquotes",
    "shortsvideo", "youtubeshortsquotes"
]

def get_seo_title(quote, author):
    template = random.choice(TITLE_TEMPLATES)
    title = template.replace("#{author}", author)
    if len(title) > 100:
        title = title[:97] + "..."
    return title

def get_description(quote, author):
    day = datetime.datetime.now().strftime("%A")
    return f'''"{quote}"
— {author}

💪 {day} Motivation — Follow for daily quotes that inspire!

🔔 Subscribe for daily motivation every morning, afternoon and evening!
👇 Share this with someone who needs it today!
💬 Comment your favorite part below!

#motivation #shorts #quotes #dailymotivation #inspirationalquotes #motivationalquotes #mindset #success #inspire #lifequotes #viral #positivevibes #selfimprovement #growthmindset #dailyquotes #successquotes #wisdomquotes'''

def post_to_youtube(video_path, quote, author):
    creds = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )

    youtube = build("youtube", "v3", credentials=creds)

    title = get_seo_title(quote, author)
    description = get_description(quote, author)
    print(f"📝 Title: {title}")

    # Upload video
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": TAGS,
                "categoryId": "22",
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
                "madeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    response = request.execute()
    video_id = response.get("id")
    print(f"✅ Video uploaded: {video_id}")

    # Upload custom thumbnail
    if video_id:
        try:
            thumbnail_path = create_thumbnail(quote, author)
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("✅ Thumbnail uploaded!")

            # Cleanup thumbnail
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)

        except Exception as e:
            print(f"⚠️ Thumbnail upload failed: {e}")

    return response
