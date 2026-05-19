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
import json

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

async def generate_voice_with_timing(text, voice, audio_path, timing_path):
    """Generate voice with timing data"""
    timing_data = []

    ssml_text = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='{voice}'>
            <prosody rate='-12%'>{text}</prosody>
        </voice>
    </speak>
    """
    communicate = edge_tts.Communicate(ssml_text, voice, is_ssml=True)

    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                timing_data.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000,
                    "duration": chunk["duration"] / 10000000
                })

    with open(timing_path, "w") as f:
        json.dump(timing_data, f)

    return timing_data

def create_youtube_short(quote, author, image_path):
    selected_voice = random.choice(VOICES)
    print(f"Voice: {selected_voice}")

    if " - " in quote:
        quote = quote.split(" - ")[0]
    if "—" in quote:
        quote = quote.split("—")[0]
    quote = quote.replace('\n', ' ').replace('"', '').strip()
    author = author.replace('-', '').replace('—', '').strip()

    tts_text = f"{quote}"
    audio_path = "quote_audio.mp3"
    timing_path = "quote_timing.json"
    voice_duration = 20
    timing_data = []

    # Step 1: Generate voice with timing
    try:
        timing_data = asyncio.run(
            generate_voice_with_timing(
                tts_text, selected_voice, audio_path, timing_path
            )
        )
        print(f"Edge TTS voice generated with {len(timing_data)} word timings!")
    except Exception as e:
        print(f"Edge TTS failed: {e} — using gTTS fallback")
        try:
            from gtts import gTTS
            tts = gTTS(text=tts_text, lang='en', slow=False, tld='com.au')
            tts.save(audio_path)
        except Exception as e2:
            print(f"gTTS also failed: {e2}")

    # Load voice and delay
    try:
        if os.path.exists(audio_path):
            voice_audio = AudioFileClip(audio_path)
            voice_duration = voice_audio.duration
            final_voice = voice_audio.with_start(VOICE_DELAY)
            print(f"Voice will start at: {VOICE_DELAY} seconds!")
        else:
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
    duration = max(VOICE_DELAY + voice_duration + 8, 45)
    duration = min(duration, 59)
    print(f"Duration: {duration} seconds")

    # Step 3: Music
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

    # Step 4: Background video
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

    animation = random.choice(ANIMATIONS)
    print(f"Animation: {animation}")

    # Step 6: Text overlays
    try:
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
        hook_clip = hook_clip.with_position(("center", 250))
        hook_clip = hook_clip.with_start(0)
        hook_clip = hook_clip.with_duration(8)
        clips.append(hook_clip)

        # Countdown 5 to 1
        for i, number in enumerate(["5\n", "4\n", "3\n", "2\n", "1\n"]):
            num_clip = TextClip(
                text=number,
                font_size=250,
                color="#FFFFFF",
                font="LiberationSans-Bold",
                method="label",
                text_align="center",
                stroke_color="white",
                stroke_width=8
            )
            num_clip = num_clip.with_position(("center", 750))
            num_clip = num_clip.with_start(
                COUNTDOWN_START + i * COUNTDOWN_EACH)
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
        go_clip = go_clip.with_position(("center", 800))
        go_clip = go_clip.with_start(
            COUNTDOWN_START + COUNTDOWN_NUMBERS * COUNTDOWN_EACH)
        go_clip = go_clip.with_duration(GO_DURATION)
        clips.append(go_clip)

        # Fallback timing if Edge TTS failed
        if not timing_data:
            print("Generating timing manually...")
            words = quote.split()
            estimated_word_duration = voice_duration / max(len(words), 1)
            for running_idx, current_word in enumerate(words):
                timing_data.append({
                    "word": current_word.strip(".,!?;:\"()[]"),
                    "start": running_idx * estimated_word_duration,
                    "duration": estimated_word_duration
                })

        # ✅ KARAOKE STYLE — Groups of 4 words, current word UPPERCASE
        if timing_data:
            print(f"Creating karaoke subtitle clips...")

            # Group words into lines of 4
            line_size = 4
            lines = []
            for i in range(0, len(timing_data), line_size):
                line_words = timing_data[i:i + line_size]
                lines.append(line_words)

            for line_words in lines:
                if not line_words:
                    continue

                line_start = line_words[0]["start"] + VOICE_DELAY

                if line_start >= duration:
                    break

                # For each word show full line with current word highlighted
                for word_idx, word_data in enumerate(line_words):
                    word_start = word_data["start"] + VOICE_DELAY
                    word_dur = max(word_data["duration"], 0.15)

                    if word_start >= duration:
                        break

                    # Build line with current word UPPERCASE yellow
                    line_parts = []
                    for j, w in enumerate(line_words):
                        if j == word_idx:
                            line_parts.append(w["word"].upper())
                        else:
                            line_parts.append(w["word"])
                    display_text = ' '.join(line_parts) + "\n\n"

                    subtitle_clip = TextClip(
                        text=display_text,
                        font_size=70,
                        color="white",
                        font="LiberationSans-Bold",
                        method="caption",
                        size=(950, None),
                        text_align="center",
                        stroke_color="black",
                        stroke_width=3
                    )
                    subtitle_clip = subtitle_clip.with_position(
                        ("center", 700))
                    subtitle_clip = subtitle_clip.with_start(word_start)
                    subtitle_clip = subtitle_clip.with_duration(word_dur)
                    clips.append(subtitle_clip)

            print(f"Karaoke clips added!")

        # Full quote after voice ends
        full_quote_start = VOICE_DELAY + voice_duration + 1.0

        if full_quote_start < duration:
            lines = quote.split('\n')
            wrapped_lines = []
            for line in lines:
                if len(line) > 25:
                    wrapped = textwrap.fill(line, width=25)
                    wrapped_lines.append(wrapped)
                else:
                    wrapped_lines.append(line)
            quote_text = '\n'.join(wrapped_lines) + '\n\n'

            q_font_size = 55 if len(quote) > 100 else 60

            full_quote_clip = TextClip(
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
            full_
