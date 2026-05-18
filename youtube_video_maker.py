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

def generate_karaoke_chunks(timing_data):
    """Groups words into sentences, then splits each sentence into cumulative word-by-word chunks."""
    sentences = []
    current_sentence = []
    
    # 1. Group words by punctuation sentences
    for w in timing_data:
        current_sentence.append(w)
        word_text = w["word"].strip()
        if word_text.endswith(('.', '!', '?')):
            sentences.append(current_sentence)
            current_sentence = []
            
    if current_sentence:
        sentences.append(current_sentence)
        
    chunks = []
    # 2. Convert sentences into cumulative word-by-word timestamps
    for s_idx, sentence in enumerate(sentences):
        if not sentence:
            continue
            
        for w_idx in range(len(sentence)):
            # Join words up to the current word index inside the active sentence
            words_up_to_now = [word["word"] for word in sentence[:w_idx + 1]]
            chunk_text = ' '.join(words_up_to_now)
            
            chunk_start = sentence[w_idx]["start"]
            
            # Determine end timing for this precise cumulative state
            if w_idx < len(sentence) - 1:
                # Changes the split visual layout when the next word starts
                chunk_end = sentence[w_idx + 1]["start"]
            else:
                # Last word of the sentence: hangs until the next sentence begins
                if s_idx < len(sentences) - 1 and sentences[s_idx + 1]:
                    chunk_end = sentences[s_idx + 1][0]["start"]
                else:
                    chunk_end = sentence[w_idx]["start"] + sentence[w_idx]["duration"] + 1.5
                    
            chunks.append({
                "text": chunk_text,
                "start": chunk_start,
                "end": chunk_end
            })
            
    return chunks

def create_youtube_short(quote, author, image_path):
    # Step 1: Generate voice with word timing
    selected_voice = random.choice(VOICES)
    print(f"Voice: {selected_voice}")

    tts_text = f"{quote}. By {author}"
    audio_path = "quote_audio.mp3"
    timing_path = "quote_timing.json"
    voice_duration = 20
    timing_data = []

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

    # Load voice and delay using with_start
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

    # Step 6: Add text overlays
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

        # ✅ SUBTITLE STYLE — Karaoke word-by-word accumulation within sentences
        if timing_data:
            print(f"Creating karaoke-style subtitle clips...")
            chunks = generate_karaoke_chunks(timing_data)

            for chunk in chunks:
                # Add VOICE_DELAY offset to sync with delayed voice
                chunk_start = chunk["start"] + VOICE_DELAY
                chunk_end = chunk["end"] + VOICE_DELAY
                chunk_dur = max(chunk_end - chunk_start, 0.1)

                # Skip if goes beyond video
                if chunk_start >= duration:
                    break

                # Wrap text nicely so it doesn't bleed out of width limits
                wrapped_text = textwrap.fill(chunk["text"], width=28) + "\n\n"

                subtitle_clip = TextClip(
                    text=wrapped_text,
                    font_size=58,
                    color="white",
                    font="LiberationSans-Bold",
                    method="caption",
                    size=(850, None),
                    text_align="center",
                    stroke_color="black",
                    stroke_width=2
                )
                subtitle_clip = subtitle_clip.with_position(("center", 700))
                subtitle_clip = subtitle_clip.with_start(chunk_start)
                subtitle_clip = subtitle_clip.with_duration(min(chunk_dur, duration - chunk_start))
                clips.append(subtitle_clip)

            print(f"Added {len(chunks)} karaoke subtitle frames!")

        else:
            # Fallback — show full quote at once if no timing data
            print("No timing data — showing full quote")
            lines = quote.split('\n')
            wrapped_lines = []
            for line in lines:
                if len(line) > 25:
                    wrapped = textwrap.fill(line, width=25)
                    wrapped_lines.append(wrapped)
                else:
                    wrapped_lines.append(line)
            quote_text = '\n'.join(wrapped_lines) + '\n\n'

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

        # Author — appears after voice finishes quote
        author_start = VOICE_DELAY + voice_duration - 3
        author_clip = TextClip(
            text=f"— {author}\n\n",
            font_size=36,
            color="#FFFFFF",
            font="DejaVuSans-Bold",
            method="caption",
            size=(700, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        author_clip = author_clip.with_position(("center", 1100))
        author_clip = author_clip.with_start(max(author_start, VOICE_DELAY))
        author_clip = author_clip.with_duration(
            duration - max(author_start, VOICE_DELAY))
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
        bell_clip = bell_clip.with_position(("center", 1200))
        bell_clip = bell_clip.with_start(duration - 5)
        bell_clip = bell_clip.with_duration(5)
        clips.append(bell_clip)

        final_video = CompositeVideoClip(clips)
        print("Subtitle style animations added!")

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
    for f in [audio_path, timing_path,
              "background_video.mp4", "vertical_quote.png"]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
