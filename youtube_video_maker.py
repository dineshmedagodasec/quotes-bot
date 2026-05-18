from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, ImageClip, AudioClip
from moviepy.audio.fx import MultiplyVolume
from PIL import Image
import edge_tts
import asyncio
import os
import random
import textwrap
import requests
import numpy as np

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
    "WAIT... read this slowly\n\n",
    "This will change how you think\n\n",
    "You NEEDED to see this today\n\n",
    "Stop scrolling. Read this.\n\n",
    "This one hits different\n\n",
    "Share this before you scroll\n\n",
    "99% of people ignore this\n\n",
    "This changed my life\n\n",
    "Read this 3 times\n\n",
    "Do NOT skip this\n\n",
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

VOICES = [
    "en-US-GuyNeural",
    "en-GB-RyanNeural",
    "en-AU-WilliamNeural",
    "en-US-AriaNeural",
    "en-GB-SoniaNeural",
]

# Countdown timing constants
COUNTDOWN_START = 1
COUNTDOWN_EACH = 1.5
COUNTDOWN_NUMBERS = 5
GO_DURATION = 1.5
QUOTE_DELAY = 2
VOICE_DELAY = COUNTDOWN_START + (COUNTDOWN_NUMBERS * COUNTDOWN_EACH) + GO_DURATION + QUOTE_DELAY

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

async def generate_voice(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_youtube_short(quote, author, image_path):
    # Step 1: Generate voice
    selected_voice = random.choice(VOICES)
    print(f"Voice: {selected_voice}")

    tts_text = f"{quote}... by {author}"
    audio_path = "quote_audio.mp3"
    voice_duration = 20  # default

    # Try Edge TTS
    try:
        asyncio.run(generate_voice(tts_text, selected_voice, audio_path))
        print("Edge TTS voice generated!")
    except Exception as e:
        print(f"Edge TTS failed: {e} — using gTTS")
        try:
            from gtts import gTTS
            tts = gTTS(text=tts_text, lang='en', slow=False, tld='com.au')
            tts.save(audio_path)
        except Exception as e2:
            print(f"gTTS also failed: {e2}")

    # Load voice and delay using with_start
    try:
        if os.path.exists(audio_path):
            voice_audio = AudioFileClip(audio_path)
            voice_duration = voice_audio.duration
            # Delay voice start by VOICE_DELAY seconds
            final_voice = voice_audio.with_start(VOICE_DELAY)
            print(f"Voice will start at: {VOICE_DELAY} seconds!")
        else:
            print("Audio file not found!")
            final_voice = AudioClip(
                make_frame=lambda t: np.zeros((2,)),
                duration=30,
                fps=44100
            )
    except Exception as e:
        print(f"Voice loading failed: {e}")
        final_voice = AudioClip(
            make_frame=lambda t: np.zeros((2,)),
            duration=30,
            fps=44100
        )

    # Step 2: Set duration
    duration = max(VOICE_DELAY + voice_duration + 3, 40)
    duration = min(duration, 59)
    print(f"Duration: {duration} seconds")

    # Step 3: Pick random music
    music_file = random.choice(MUSIC_FILES)
    print(f"Music: {music_file}")

    try:
        music_clip = AudioFileClip(music_file)
        music_clip = music_clip.subclipped(0, duration)
        music_clip = music_clip.with_effects([MultiplyVolume(0.15)])
        final_audio = CompositeAudioClip([music_clip, final_voice])
    except Exception as e:
        print(f"Music failed: {e}")
        final_audio = final_voice

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

    # Step 6: Add text overlays with countdown
    try:
        lines = quote.split('\n')
        wrapped_lines = []
        for line in lines:
            if len(line) > 25:
                wrapped = textwrap.fill(line, width=25)
                wrapped_lines.append(wrapped)
            else:
                wrapped_lines.append(line)
        quote_text = '\n'.join(wrapped_lines) + '\n\n'

        clips = [video]

        # Hook text
        hook_text = random.choice(HOOKS)
        hook_clip = TextClip(
            text=hook_text,
            font_size=42,
            color="#FFD700",
            font="DejaVuSans",
            method="caption",
            size=(750, None),
            text_align="center",
            stroke_color="black",
            stroke_width=2
        )
        hook_clip = hook_clip.with_position(("center", 150))
        hook_clip = hook_clip.with_start(0)
        hook_clip = hook_clip.with_duration(8)
        clips.append(hook_clip)

        # Countdown 5 to 1
        countdown_colors = [
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF",
        ]

        for i, number in enumerate(["5\n", "4\n", "3\n", "2\n", "1\n"]):
            num_clip = TextClip(
                text=number,
                font_size=250,
                color=countdown_colors[i],
                font="LiberationSans-Bold",
                method="label",
                text_align="center",
                stroke_color="black",
                stroke_width=8
            )
            num_clip = num_clip.with_position(("center", 650))
            num_clip = num_clip.with_start(COUNTDOWN_START + i * COUNTDOWN_EACH)
            num_clip = num_clip.with_duration(COUNTDOWN_EACH)
            clips.append(num_clip)

        # GO!
        go_clip = TextClip(
            text="GO!\n",
            font_size=200,
            color="#00FF00",
            font="LiberationSans-Bold",
            method="label",
            text_align="center",
            stroke_color="black",
            stroke_width=8
        )
        go_clip = go_clip.with_position(("center", 650))
        go_clip = go_clip.with_start(
            COUNTDOWN_START + COUNTDOWN_NUMBERS * COUNTDOWN_EACH)
        go_clip = go_clip.with_duration(GO_DURATION)
        clips.append(go_clip)

        # Quote appears after countdown
        quote_start = VOICE_DELAY
        if len(quote) > 100:
            q_font_size = 40
        else:
            q_font_size = 55

        quote_clip = TextClip(
            text=quote_text,
            font_size=q_font_size,
            color="white",
            font="LiberationSans-Bold",
            method="caption",
            size=(750, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        quote_clip = apply_animation(quote_clip, animation, 500)
        quote_clip = quote_clip.with_start(quote_start)
        quote_clip = quote_clip.with_duration(duration - quote_start)
        clips.append(quote_clip)

        # Author
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
        author_clip = author_clip.with_start(quote_start + 2)
        author_clip = author_clip.with_duration(duration - quote_start - 2)
        clips.append(author_clip)

        # Subscribe watermark
        channel_clip = TextClip(
            text="Subscribe for daily quotes\n\n",
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
        clips.append(channel_clip)

        # End screen
        end_screen_clip = TextClip(
            text="NEW VIDEO EVERY DAY\nSubscribe Now\n",
            font_size=48,
            color="#FFD700",
            font="DejaVuSans-Bold",
            method="caption",
            size=(750, None),
            text_align="center",
            stroke_color="black",
            stroke_width=2
        )
        end_screen_clip = end_screen_clip.with_position(("center", 800))
        end_screen_clip = end_screen_clip.with_start(duration - 5)
        end_screen_clip = end_screen_clip.with_duration(5)
        clips.append(end_screen_clip)

        # Bell reminder
        bell_clip = TextClip(
            text="Turn on notifications\nso you never miss a quote\n",
            font_size=32,
            color="white",
            font="DejaVuSans",
            method="caption",
            size=(700, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        bell_clip = bell_clip.with_position(("center", 1100))
        bell_clip = bell_clip.with_start(duration - 5)
        bell_clip = bell_clip.with_duration(5)
        clips.append(bell_clip)

        final_video = CompositeVideoClip(clips)
        print("Countdown + animations added!")

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

    # Cleanup
    for f in [audio_path, "background_video.mp4", "vertical_quote.png"]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
