from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, ImageClip
from moviepy.audio.fx import MultiplyVolume
from PIL import Image
import edge_tts
import asyncio
import os
import random
import requests
import textwrap

MUSIC_FILES = [
    "music/music_1.mp3",
    "music/music_2.mp3",
    "music/music_3.mp3",
    "music/music_4.mp3",
    "music/music_5.mp3",
    "music/music_6.mp3",
    "music/music_7.mp3",
]

SEARCH_KEYWORDS = [
    "city timelapse",
    "mountain sunrise",
    "ocean waves",
    "forest peaceful",
    "stars night sky",
]

COUNTDOWN_SCRIPTS = [
    {
        "hook": "Your brain will kill\nyour idea in 5 seconds",
        "countdown_text": "Count with me...",
        "message": "The moment you have\nan instinct to act\nYou MUST move NOW\nOr your brain kills it",
        "cta": "5 seconds is all you need\nStart YOUR plan NOW",
        "voice_text": "Your brain will kill your idea in 5 seconds. Count with me. 5. 4. 3. 2. 1. Go! The moment you have an instinct to act, you must move now. Or your brain kills it. 5 seconds is all you need. Start your plan now."
    },
    {
        "hook": "Stop waiting\nfor the right moment",
        "countdown_text": "The right moment is NOW",
        "message": "Every second you wait\nyou lose momentum\nSuccess favors those\nwho act FAST",
        "cta": "Your dream is waiting\nStart in 5 seconds",
        "voice_text": "Stop waiting for the right moment. The right moment is NOW. Every second you wait, you lose momentum. Success favors those who act fast. Your dream is waiting. Start in 5 seconds. 5. 4. 3. 2. 1. Go!"
    },
    {
        "hook": "You have been putting\nthis off too long",
        "countdown_text": "No more excuses...",
        "message": "Fear is just excitement\nwithout breath\nTake a deep breath\nAnd JUMP",
        "cta": "No more waiting\nYour time is NOW",
        "voice_text": "You have been putting this off too long. No more excuses. Fear is just excitement without breath. Take a deep breath and jump. No more waiting. Your time is now. 5. 4. 3. 2. 1. Go!"
    },
    {
        "hook": "One decision can\nchange your entire life",
        "countdown_text": "Make it NOW...",
        "message": "You are one decision\naway from a completely\ndifferent life\nWhat are you waiting for?",
        "cta": "Make the decision\nRight NOW",
        "voice_text": "One decision can change your entire life. Make it now. You are one decision away from a completely different life. What are you waiting for? Make the decision right now. 5. 4. 3. 2. 1. Go!"
    },
    {
        "hook": "Procrastination is\nstealing your future",
        "countdown_text": "Take it back...",
        "message": "Every day you delay\nis a day you can never\nget back\nYour future self is\nbegging you to START",
        "cta": "Do it for your\nfuture self",
        "voice_text": "Procrastination is stealing your future. Take it back. Every day you delay is a day you can never get back. Your future self is begging you to start. Do it for your future self. 5. 4. 3. 2. 1. Go!"
    },
]

VOICES = [
    "en-US-GuyNeural",
    "en-GB-RyanNeural",
    "en-AU-WilliamNeural",
]

def get_pexels_video():
    api_key = os.getenv("PEXELS_API_KEY")
    keyword = random.choice(SEARCH_KEYWORDS)
    print(f"Searching video: {keyword}")

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
            video_path = "bg_countdown_video.mp4"
            with open(video_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return video_path

    except Exception as e:
        print(f"Pexels failed: {e}")
        return None

async def generate_voice(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_countdown_video():
    script = random.choice(COUNTDOWN_SCRIPTS)
    voice = random.choice(VOICES)

    print(f"Creating countdown video: {script['hook'][:30]}")

    # Generate voice
    audio_path = "countdown_audio.mp3"
    try:
        asyncio.run(generate_voice(script["voice_text"], voice, audio_path))
        print("Voice generated!")
    except Exception as e:
        print(f"Voice failed: {e}")
        from gtts import gTTS
        tts = gTTS(text=script["voice_text"], lang='en', slow=False)
        tts.save(audio_path)

    # Load audio
    voice_clip = AudioFileClip(audio_path)
    duration = max(voice_clip.duration + 2, 35)
    duration = min(duration, 59)

    # Music
    music_file = random.choice(MUSIC_FILES)
    try:
        music_clip = AudioFileClip(music_file)
        music_clip = music_clip.subclipped(0, duration)
        music_clip = music_clip.with_effects([MultiplyVolume(0.12)])
        final_audio = CompositeAudioClip([music_clip, voice_clip])
    except:
        final_audio = voice_clip

    # Background video
    bg_path = get_pexels_video()
    video = None

    if bg_path:
        try:
            bg_video = VideoFileClip(bg_path)
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
            ).with_opacity(0.6)
            video = CompositeVideoClip([bg_video, overlay])
            video = video.with_audio(final_audio)
        except Exception as e:
            print(f"Video failed: {e}")
            video = None

    if video is None:
        bg = Image.new("RGB", (1080, 1920), color=(10, 10, 20))
        bg.save("countdown_bg.png")
        video = ImageClip("countdown_bg.png", duration=duration)
        video = video.with_audio(final_audio)

    # Build text clips
    clips = [video]

    # Hook text — appears at start
    hook_clip = TextClip(
        text=f"{script['hook']}\n\n",
        font_size=58,
        color="#FFD700",
        font="LiberationSans-Bold",
        method="caption",
        size=(800, None),
        text_align="center",
        stroke_color="black",
        stroke_width=2
    )
    hook_clip = hook_clip.with_position(("center", 300))
    hook_clip = hook_clip.with_start(0)
    hook_clip = hook_clip.with_duration(4)
    clips.append(hook_clip)

    # Countdown text
    countdown_clip = TextClip(
        text=f"{script['countdown_text']}\n\n",
        font_size=40,
        color="white",
        font="DejaVuSans",
        method="caption",
        size=(750, None),
        text_align="center",
        stroke_color="black",
        stroke_width=1
    )
    countdown_clip = countdown_clip.with_position(("center", 600))
    countdown_clip = countdown_clip.with_start(3)
    countdown_clip = countdown_clip.with_duration(3)
    clips.append(countdown_clip)

    # BIG countdown numbers 5 to 1
    countdown_start = 6
    colors = ["#FF0000", "#FF4500", "#FF8C00", "#FFD700", "#00FF00"]

    for i, number in enumerate(["5", "4", "3", "2", "1"]):
        num_clip = TextClip(
            text=number,
            font_size=300,
            color=colors[i],
            font="LiberationSans-Bold",
            method="label",
            text_align="center",
            stroke_color="black",
            stroke_width=8
        )
        num_clip = num_clip.with_position(("center", 650))
        num_clip = num_clip.with_start(countdown_start + i * 1.5)
        num_clip = num_clip.with_duration(1.5)
        clips.append(num_clip)

    # GO! text
    go_clip = TextClip(
        text="GO!",
        font_size=250,
        color="#00FF00",
        font="LiberationSans-Bold",
        method="label",
        text_align="center",
        stroke_color="black",
        stroke_width=8
    )
    go_clip = go_clip.with_position(("center", 700))
    go_clip = go_clip.with_start(countdown_start + 5 * 1.5)
    go_clip = go_clip.with_duration(2)
    clips.append(go_clip)

    # Message after countdown
    msg_start = countdown_start + 5 * 1.5 + 2
    wrapped_msg = textwrap.fill(script["message"], width=25)
    msg_clip = TextClip(
        text=wrapped_msg + "\n\n",
        font_size=52,
        color="white",
        font="LiberationSans-Bold",
        method="caption",
        size=(800, None),
        text_align="center",
        stroke_color="black",
        stroke_width=1
    )
    msg_clip = msg_clip.with_position(("center", 500))
    msg_clip = msg_clip.with_start(msg_start)
    msg_clip = msg_clip.with_duration(duration - msg_start - 5)
    clips.append(msg_clip)

    # CTA at end
    cta_clip = TextClip(
        text=script["cta"] + "\n\n",
        font_size=42,
        color="#FFD700",
        font="DejaVuSans-Bold",
        method="caption",
        size=(750, None),
        text_align="center",
        stroke_color="black",
        stroke_width=1
    )
    cta_clip = cta_clip.with_position(("center", 900))
    cta_clip = cta_clip.with_start(duration - 8)
    cta_clip = cta_clip.with_duration(8)
    clips.append(cta_clip)

    # Subscribe watermark
    sub_clip = TextClip(
        text="Subscribe for daily motivation\n\n",
        font_size=26,
        color="white",
        font="DejaVuSans-Bold",
        method="caption",
        size=(700, None),
        text_align="center",
        stroke_color="black",
        stroke_width=1
    )
    sub_clip = sub_clip.with_position(("center", 1750))
    sub_clip = sub_clip.with_start(0)
    sub_clip = sub_clip.with_duration(duration)
    clips.append(sub_clip)

    # Combine all
    final_video = CompositeVideoClip(clips)

    output_path = "countdown_short.mp4"
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    # Cleanup
    for f in [audio_path, "bg_countdown_video.mp4", "countdown_bg.png"]:
        if os.path.exists(f):
            os.remove(f)

    return output_path, script["hook"], script["cta"]
