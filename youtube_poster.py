import os
import random
import datetime
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from thumbnail_maker import create_thumbnail

# Big hashtags
BIG_TAGS = [
    "motivation", "shorts", "quotes", "viral",
    "inspirationalquotes", "motivationalquotes",
    "success", "mindset", "inspire", "lifequotes",
]

# Medium hashtags
MEDIUM_TAGS = [
    "dailymotivation", "positivevibes", "selfimprovement",
    "growthmindset", "dailyquotes", "successquotes",
    "wisdomquotes", "morningmotivation", "motivationaldaily",
    "quoteoftheday",
]

# Small niche hashtags
SMALL_TAGS = [
    "dailyquotesforlife", "motivationforlife",
    "quotestoinspire", "shortsmotivation",
    "motivationalshorts", "quotesdaily",
    "lifeinspiration", "successmindset",
    "positivequotes", "inspirationoftheday",
]

# Day specific hashtags
DAY_TAGS = {
    "Monday": ["mondaymotivation", "mondaymindset", "newweek"],
    "Tuesday": ["tuesdaymotivation", "tuesdaythoughts"],
    "Wednesday": ["wednesdaywisdom", "midweek"],
    "Thursday": ["thursdaythoughts", "thursdaymotivation"],
    "Friday": ["fridaymotivation", "fridayfeeling", "tgif"],
    "Saturday": ["saturdaymotivation", "weekend"],
    "Sunday": ["sundaymotivation", "sundayvibes", "newweek"],
}

TITLE_TEMPLATES = [
    "POV You needed to hear this #{author}",
    "That hit different #{author}",
    "No one talks about this enough",
    "This is why you are not succeeding yet",
    "The harsh truth about success #{author}",
    "Stop doing this if you want to succeed",
    "This will hurt but you need to hear it",
    "Why most people never succeed",
    "The secret nobody tells you about success",
    "This changed everything #{author}",
    "This Will Change Your Life #{author}",
    "Words That Will Give You Chills #{author}",
    "Morning Motivation That Hits Different",
    "The Most Powerful Quote You Will Hear Today",
    "Powerful Words For A Powerful Life",
]

TAGS = [
    "motivation", "shorts", "quotes", "dailymotivation",
    "inspirationalquotes", "motivationalquotes", "mindset",
    "success", "inspire", "lifequotes", "viral", "positivevibes",
    "selfimprovement", "growthmindset", "dailyquotes",
    "motivationalspeech", "successquotes", "wisdomquotes",
    "shortsvideo", "youtubeshortsquotes"
]

COMMUNITY_POLLS = [
    {
        "text": "What time do you watch motivation videos?",
        "choices": ["Morning - rise and grind!", "Afternoon break", "Evening wind down", "Late night hustle"]
    },
    {
        "text": "What stops you from reaching your goals?",
        "choices": ["Fear of failure", "Lack of motivation", "No clear plan", "Other"]
    },
    {
        "text": "Which quote type hits different for you?",
        "choices": ["Success quotes", "Life wisdom quotes", "Love and relationships", "Hustle and grind"]
    },
    {
        "text": "How do you start your morning?",
        "choices": ["Motivation videos", "Exercise", "Meditation", "Just coffee!"]
    },
    {
        "text": "What is your biggest goal right now?",
        "choices": ["Financial freedom", "Better health", "Better relationships", "Personal growth"]
    },
    {
        "text": "How many motivational videos do you watch daily?",
        "choices": ["1-2 videos", "3-5 videos", "5+ videos", "First time here!"]
    },
    {
        "text": "Which day do you need motivation most?",
        "choices": ["Monday - hardest day!", "Wednesday - mid week slump", "Friday - almost there!", "Everyday!"]
    },
]

def get_seo_title(quote, author):
    template = random.choice(TITLE_TEMPLATES)
    title = template.replace("#{author}", author)
    if len(title) > 100:
        title = title[:97] + "..."
    return title

def get_description(quote, author):
    day = datetime.datetime.now().strftime("%A")

    selected_big = random.sample(BIG_TAGS, 5)
    selected_medium = random.sample(MEDIUM_TAGS, 5)
    selected_small = random.sample(SMALL_TAGS, 4)
    selected_day = DAY_TAGS.get(day, ["motivation"])

    all_hashtags = selected_big + selected_medium + selected_small + selected_day
    hashtag_string = ' '.join([f"#{tag}" for tag in all_hashtags])

    return f'''"{quote}"
— {author}

Comment YES if this hit different!
Tag someone who needs to hear this today!

{day} Motivation — Subscribe for daily quotes!
New videos every morning afternoon and evening!

{hashtag_string}'''

def add_to_playlist(youtube, video_id, quote, author):
    playlist_id = None
    quote_lower = quote.lower()
    day = datetime.datetime.now().strftime("%A")

    if "?" in quote or "A)" in quote:
        playlist_id = os.getenv("YT_PLAYLIST_QUESTIONS")
    elif day in ["Monday", "Tuesday", "Wednesday"]:
        playlist_id = os.getenv("YT_PLAYLIST_MOTIVATION")
    elif any(word in quote_lower for word in
             ["success", "achieve", "win", "goal",
              "work", "hustle", "dream"]):
        playlist_id = os.getenv("YT_PLAYLIST_SUCCESS")
    elif any(word in quote_lower for word in
             ["life", "live", "change", "world",
              "love", "heart", "soul"]):
        playlist_id = os.getenv("YT_PLAYLIST_LIFE")
    else:
        playlist_id = os.getenv("YT_PLAYLIST_MORNING")

    if playlist_id:
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()
            print(f"Added to playlist!")
        except Exception as e:
            print(f"Playlist add failed: {e}")

def post_community_poll(youtube):
    try:
        poll = random.choice(COMMUNITY_POLLS)
        print(f"Posting community poll: {poll['text']}")

        youtube.communityPosts().insert(
            part="snippet",
            body={
                "snippet": {
                    "type": "pollPost",
                    "pollPost": {
                        "question": {
                            "text": poll["text"]
                        },
                        "choices": [
                            {"text": choice} for choice in poll["choices"]
                        ]
                    }
                }
            }
        ).execute()
        print("Community poll posted!")

    except Exception as e:
        print(f"Community poll failed: {e}")

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
    print(f"Title: {title}")

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
    print(f"Video uploaded: {video_id}")

    # Add to playlist
    if video_id:
        add_to_playlist(youtube, video_id, quote, author)

    # Upload custom thumbnail
    if video_id:
        try:
            thumbnail_path = create_thumbnail(quote, author)
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded!")
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except Exception as e:
            print(f"Thumbnail upload failed: {e}")

    return response
