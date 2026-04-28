from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, ImageClip
from moviepy.audio.fx import MultiplyVolume
from PIL import Image
from gtts import gTTS
import os
import random
import textwrap
import requests

MUSIC_FILES = [
    "music/music_1.mp3",
    "music/music_2.mp3",
    "music/music_3.mp3",
    "music/music_4.mp3",
    "music/music_5.mp3",
    "music/music_6.mp3",
    "music/music_7.mp3",
]

ANIMATIONS = ["slide_up", "slide_down", "slide_left", "bounce"]

HOOKS = [
    "Stop scrolling — this will change your day \n\n",
    "This quote will hit different today \n\n",
    "You needed to hear this today \n\n",
    "Read this slowly... it's powerful \n\n",
    "This one stopped me in my tracks \n\n",
    "Share this with someone who needs it \n\n",
    "This changed my perspective forever \n\n",
    "The most powerful quote you'll hear today \n\n",
    "Read this every morning \n\n",
    "This will give you chills \n\n",
]

SEARCH_KEYWORDS = [
    "nature sunset",
    "ocean waves",
    "mountain sunrise",
    "forest peaceful",
    "sky clouds",
    "waterfall nature",
    "city timelapse",
    "stars night sky",
    "flowers blooming",
    "river flowing"
]

def get_pexels_video(quote):
    api_key = os.getenv("PEXELS_API_KEY")
    keyword = random.choice(SEARCH_KEYWORDS)
    print(f"Searching video for: {keyword}")

    url = f"https://api.pexels.com/videos/search?query={keyword}&orientation=portrait&size=medium&per_page=10"
    headers = {"Authorization": api_key}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        videos = data.get("videos", [])
        if not videos:
            return None

        video = random.choice(videos)
        video_files = video.get("video_files", [])
        best_file = None
        for vf in video_files:
            if vf.get("quality") in ["hd", "sd"]:
                best_file = vf
                break
        if not best_file and video_files:
            best_file = video_files[0]

        if best_file:
            print(f"Downloading video...")
            video_response = requests.get(best_file["link"], stream=True)
            video_path = "background_video.mp4"
            with open(video_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return video_path

    except Exception as e:
        print(f"Pexels failed: {e}")
        return None

def apply_animation(clip, animation, base_y):
    if animation == "slide_up":
        clip = clip.with_position(
            lambda t: ("center", max(base_y, base_y + 200 - int(t * 150)))
            if t < 1.5 else ("center", base_y)
        )
    elif animation == "slide_down":
        clip = clip.with_position(
            lambda t: ("center", max(base_y - 200, base_y - 200 + int(t * 150)))
            if t < 1.5 else ("center", base_y)
        )
    elif animation == "slide_left":
        clip = clip.with_position(
            lambda t: (max(0, 1080 - int(t * 800)), base_y)
            if t < 1.5 else ("center", base_y)
        )
    elif animation == "bounce":
        def bounce_pos(t):
            if t < 0.3:
                return ("center", base_y - int(t * 400))
            elif t < 0.6:
                return ("center", base_y - 120 + int((t - 0.3) * 400))
            elif t < 0.8:
                return ("center", base_y + int((t - 0.6) * 200))
            elif t < 1.0:
                return ("center", base_y + 40 - int((t - 0.8) * 200))
            else:
                return ("center", base_y)
        clip = clip.with_position(bounce_pos)
    else:
        clip = clip.with_position(("center", base_y))
    return clip

def create_youtube_short(quote, author, image_path):
    # Step 1: Generate voice audio
    tts_text = f"{quote}... by {author}"
    tts = gTTS(text=tts_text, lang='en', slow=False, tld='com.au')
    audio_path = "quote_audio.mp3"
    tts.save(audio_path)

    # Step 2: Load voice audio
    voice_clip = AudioFileClip(audio_path)
    duration = max(voice_clip.duration + 2, 30)
    duration = min(duration, 59)

    # Step 3: Pick random music
    music_file = random.choice(MUSIC_FILES)
    print(f"Music: {music_file}")

    try:
        music_clip = AudioFileClip(music_file)
        music_clip = music_clip.subclipped(0, duration)
        music_clip = music_clip.with_effects([MultiplyVolume(0.15)])
        final_audio = CompositeAudioClip([music_clip, voice_clip])
    except Exception as e:
        print(f"Music failed: {e}")
        final_audio = voice_clip

    # Step 4: Get background video
    bg_video_path = get_pexels_video(quote)
    video = None

    if bg_video_path:
        try:
            bg_video = VideoFileClip(bg_video_path)
            if bg_video.duration < duration:
                loops = int(duration / bg_video.duration) + 1
                bg_video = concatenate_videoclips([bg_video] * loops)
            bg_video = bg_video.subclipped(0, duration)
            bg_video = bg_video.resized(height=1920)
            x_center = bg_video.w / 2
            bg_video = bg_video.cropped(
                x1=x_center - 540,
                x2=x_center + 540,
                y1=0,
                y2=1920
            )
            overlay = ColorClip(
                size=(1080, 1920),
                color=[0, 0, 0],
                duration=duration
            ).with_opacity(0.5)
            video = CompositeVideoClip([bg_video, overlay])
            video = video.with_audio(final_audio)
            print("Background video loaded!")
        except Exception as e:
            print(f"Video failed: {e}")
            video = None

    if video is None:
        img = Image.open(image_path)
        img_resized = img.resize((1080, 1920))
        vertical_path = "vertical_quote.png"
        img_resized.save(vertical_path)
        video = ImageClip(vertical_path, duration=duration)
        video = video.with_audio(final_audio)
        print("Using static image!")

    # Step 5: Pick random animation
    animation = random.choice(ANIMATIONS)
    print(f"Animation: {animation}")

    # Step 6: Add text overlays
    try:
        wrapped_quote = textwrap.fill(quote, width=27)
        quote_text = f'"{wrapped_quote}"\n\n'

        # Hook text
        hook_text = random.choice(HOOKS)
        hook_clip = TextClip(
            text=hook_text,
            font_size=38,
            color="#FFD700",
            font="DejaVuSans",
            method="caption",
            size=(750, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        hook_clip = hook_clip.with_position(("center", 200))
        hook_clip = hook_clip.with_start(0)
        hook_clip = hook_clip.with_duration(10)

        # Quote text
        quote_clip = TextClip(
            text=quote_text,
            font_size=55,
            color="white",
            font="LiberationSans-Bold",
            method="caption",
            size=(750, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        quote_clip = apply_animation(quote_clip, animation, 500)
        quote_clip = quote_clip.with_start(1)
        quote_clip = quote_clip.with_duration(duration - 1)

        # Author text
        author_clip = TextClip(
            text=f"— {author}\n\n",
            font_size=32,
            color="#FFD700",
            font="DejaVuSans",
            method="caption",
            size=(700, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        author_clip = apply_animation(author_clip, animation, 1200)
        author_clip = author_clip.with_start(3)
        author_clip = author_clip.with_duration(duration - 3)

        # Subscribe watermark
        channel_clip = TextClip(
            text="Subscribe for daily quotes \n\n",
            font_size=26,
            color="white",
            font="DejaVuSans-Bold",
            method="caption",
            size=(700, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        channel_clip = channel_clip.with_position(("center", 1550))
        channel_clip = channel_clip.with_start(0)
        channel_clip = channel_clip.with_duration(duration)

        final_video = CompositeVideoClip([
            video,
            hook_clip,
            quote_clip,
            author_clip,
            channel_clip
        ])
        print("Text animations added!")

    except Exception as e:
        print(f"Text animation failed: {e}")
        final_video = video

    output_path = "youtube_short.mp4"
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    for f in [audio_path, "background_video.mp4", "vertical_quote.png"]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
