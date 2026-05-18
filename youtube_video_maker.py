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
    """Generate voice and capture word timing data"""
    timing_data = []
    communicate = edge_tts.Communicate(text, voice)

    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                timing_data.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000,  # Convert to seconds
                    "duration": chunk["duration"] / 10000000
                })

    # Save timing data
    with open(timing_path, "w") as f:
        json.dump(timing_data, f)

    return timing_data

def split_into_chunks(timing_data, words_per_chunk=2):
    """Split words into fast, punchy karaoke-style subtitle chunks"""
    chunks = []
    i = 0
    while i < len(timing_data):
        chunk_words = timing_data[i:i + words_per_chunk]
        if chunk_words:
            chunk_text = ' '.join([w["word"] for w in chunk_words]).upper()
            chunk_start = chunk_words[0]["start"]
            chunk_end = chunk_words[-1]["start"] + chunk_words[-1]["duration"]
            chunks.append({
                "text": chunk_text,
                "start": chunk_start,
                "end": chunk_end,
                "duration": chunk_end - chunk_start
            })
        i += words_per_chunk
    return chunks

def create_youtube_short(quote, author, image_path):
    selected_voice = random.choice(VOICES)
    print(f"Voice: {selected_voice}")

    # Temporary step file paths
    quote_audio_path = "quote_only.mp3"
    author_audio_path = "author_only.mp3"
    timing_path = "quote_timing.json"
    
    quote_duration = 0
    author_duration = 0
    timing_data = []

    # Step 1: Generate separate audio streams so karaoke features ONLY affect the quote
    try:
        # Generate quote with explicit timestamp data
        timing_data = asyncio.run(
            generate_voice_with_timing(quote, selected_voice, quote_audio_path, timing_path)
        )
        print(f"Edge TTS quote generated with {len(timing_data)} word timings!")
        
        # Generate author audio separately (no karaoke timing parsing needed)
        communicate_author = edge_tts.Communicate(f"By {author}", selected_voice)
        asyncio.run(communicate_author.save(author_audio_path))
        
    except Exception as e:
        print(f"Edge TTS failed: {e} — using gTTS fallback")
        try:
            from gtts import gTTS
            tts_full = gTTS(text=f"{quote}. By {author}", lang='en', slow=False)
            tts_full.save(quote_audio_path)
        except Exception as e2:
            print(f"gTTS also failed: {e2}")

    # Build the combined voice audio sequence
    audio_clips_to_mix = []
    try:
        if os.path.exists(quote_audio_path):
            q_audio = AudioFileClip(quote_audio_path)
            quote_duration = q_audio.duration
            # Align quote start with global layout delays
            audio_clips_to_mix.append(q_audio.with_start(VOICE_DELAY))
            
            if os.path.exists(author_audio_path):
                a_audio = AudioFileClip(author_audio_path)
                author_duration = a_audio.duration
                # Play author name 0.5s after the quote vocal finishes
                author_start_time = VOICE_DELAY + quote_duration + 0.5
                audio_clips_to_mix.append(a_audio.with_start(author_start_time))
                
            final_voice = CompositeAudioClip(audio_clips_to_mix)
        else:
            final_voice = AudioClip(make_frame=lambda t: np.zeros((2,)), duration=30, fps=44100)
    except Exception as e:
        print(f"Voice arrangement preparation failed: {e}")
        final_voice = AudioClip(make_frame=lambda t: np.zeros((2,)), duration=30, fps=44100)

    # Step 2: Set absolute video duration bounded to YouTube limits
    total_voice_sequence = quote_duration + author_duration + 0.5
    duration = max(VOICE_DELAY + total_voice_sequence + 4, 40)
    duration = min(duration, 59)
    print(f"Target Duration: {duration} seconds")

    # Step 3: Mix background audio tracking tracks
    music_file = random.choice(MUSIC_FILES)
    print(f"Music audio background file: {music_file}")

    try:
        music_clip = AudioFileClip(music_file)
        music_clip = music_clip.subclipped(0, duration)
        music_clip = music_clip.with_effects([MultiplyVolume(0.15)])
        final_audio = CompositeAudioClip([music_clip, final_voice])
    except Exception as e:
        print(f"Music failed mixing parameters: {e}")
        final_audio = final_voice

    # Step 4: Video feed assignment layers
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
            bg_video = bg_video.cropped(x1=x_center - 540, x2=x_center + 540, y1=0, y2=1920)
            
            overlay = ColorClip(size=(1080, 1920), color=[0, 0, 0], duration=duration).with_opacity(0.5)
            video = CompositeVideoClip([bg_video, overlay]).with_audio(final_audio)
            print("Background asset pipeline completed successfully!")
        except Exception as e:
            print(f"Video parser system execution fault: {e}")
            video = None

    if video is None:
        img = Image.open(image_path)
        img_resized = img.resize((1080, 1920))
        vertical_path = "vertical_quote.png"
        img_resized.save(vertical_path)
        video = ImageClip(vertical_path, duration=duration).with_audio(final_audio)
        print("Fallback tracking execution: Static image frame deployed.")

    animation = random.choice(ANIMATIONS)

    # Step 6: Layout Compositing & Rendering
    try:
        clips = [video]

        # Intro Hook overlay
        hook_text = random.choice(HOOKS)
        hook_clip = TextClip(
            text=hook_text, font_size=42, color="#FFD700", font="DejaVuSans",
            method="caption", size=(750, None), text_align="center",
            stroke_color="black", stroke_width=2
        ).with_position(("center", 250)).with_start(0).with_duration(8)
        clips.append(hook_clip)

        # Countdown 5 to 1 sequence engine
        for i, number in enumerate(["5\n", "4\n", "3\n", "2\n", "1\n"]):
            num_clip = TextClip(
                text=number, font_size=250, color="#FFFFFF", font="LiberationSans-Bold",
                method="label", text_align="center", stroke_color="white", stroke_width=8
            ).with_position(("center", 750)).with_start(COUNTDOWN_START + i * COUNTDOWN_EACH).with_duration(COUNTDOWN_EACH)
            clips.append(num_clip)

        # GO Graphic overlay
        go_clip = TextClip(
            text="GO!\n", font_size=200, color="#00FF00", font="LiberationSans-Bold",
            method="label", text_align="center", stroke_color="black", stroke_width=8
        ).with_position(("center", 800)).with_start(COUNTDOWN_START + COUNTDOWN_NUMBERS * COUNTDOWN_EACH).with_duration(GO_DURATION)
        clips.append(go_clip)

        # ✅ FIXED KARAOKE ENGINE — Feeds 1-2 words sequentially based strictly on active vocal timeline
        if timing_data:
            print(f"Processing subtitle matrix mapping segments...")
            chunks = split_into_chunks(timing_data, words_per_chunk=2)

            for chunk in chunks:
                chunk_start = chunk["start"] + VOICE_DELAY
                chunk_dur = max(chunk["duration"], 0.3)

                if chunk_start >= duration:
                    break

                subtitle_clip = TextClip(
                    text=chunk["text"], font_size=75, color="white", font="LiberationSans-Bold",
                    method="caption", size=(900, None), text_align="center",
                    stroke_color="black", stroke_width=4
                ).with_position(("center", "center")).with_start(chunk_start).with_duration(chunk_dur)
                
                clips.append(subtitle_clip)
            print(f"Successfully generated {len(chunks)} isolated phrase segments!")
        else:
            # Full block text fail-safe fallback channel
            print("Subtitle dataset timeline empty. Activating baseline block rendering.")
            lines = quote.split('\n')
            wrapped_lines = [textwrap.fill(l, width=25) if len(l) > 25 else l for l in lines]
            quote_text = '\n'.join(wrapped_lines) + '\n\n'
            q_font_size = 55 if len(quote) > 100 else 60

            quote_clip = TextClip(
                text=quote_text, font_size=q_font_size, color="white", font="LiberationSans-Bold",
                method="caption", size=(750, None), text_align="center", stroke_color="black", stroke_width=1
            )
            quote_clip = apply_animation(quote_clip, animation, 450).with_start(VOICE_DELAY).with_duration(duration - VOICE_DELAY)
            clips.append(quote_clip)

        # Author bottom banner configuration display
        author_start = VOICE_DELAY + quote_duration + 0.3
        author_clip = TextClip(
            text=f"— {author}\n\n", font_size=36, color="#FFD700", font="DejaVuSans-Bold",
            method="caption", size=(700, None), text_align="center", stroke_color="black", stroke_width=1
        ).with_position(("center", 1100)).with_start(max(author_start, VOICE_DELAY)).with_duration(duration - max(author_start, VOICE_DELAY))
        clips.append(author_clip)

        # Fixed bottom watermarking banner display
        channel_clip = TextClip(
            text="Subscribe for daily quotes\n\n", font_size=26, color="white", font="DejaVuSans-Bold",
            method="caption", size=(700, None), text_align="center", stroke_color="black", stroke_width=1
        ).with_position(("center", 1600)).with_start(0).with_duration(duration)
        clips.append(channel_clip)

        # System Outro Graphic Screen
        end_screen_clip = TextClip(
            text="NEW VIDEO EVERY DAY\nSubscribe Now\n", font_size=48, color="#FFD700", font="DejaVuSans-Bold",
            method="caption", size=(750, None), text_align="center", stroke_color="black", stroke_width=2
        ).with_position(("center", 900)).with_start(duration - 5).with_duration(5)
        clips.append(end_screen_clip)

        # System End-screen notification reminder alert
        bell_clip = TextClip(
            text="Turn on notifications\nso you never miss a quote\n", font_size=32, color="white", font="DejaVuSans",
            method="caption", size=(700, None), text_align="center", stroke_color="black", stroke_width=1
        ).with_position(("center", 1300)).with_start(duration - 5).with_duration(5)
        clips.append(bell_clip)

        final_video = CompositeVideoClip(clips)

    except Exception as e:
        print(f"Overlay mapping script fault intercepted: {e}")
        final_video = video

    output_path = "youtube_short.mp4"
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    # File array system cleanup
    for f in [quote_audio_path, author_audio_path, timing_path, "background_video.mp4", "vertical_quote.png"]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
