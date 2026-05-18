from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip, ColorClip, concatenate_videoclips, ImageClip, AudioClip
from moviepy.audio.fx import MultiplyVolume
from PIL import Image
import edge_tts
import asyncio
import os
import random
import requests
import numpy as np
import json

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

MUSIC_FILES = ["music/music_1.mp3", "music/music_2.mp3", "music/music_3.mp3"]
VOICES = ["en-US-GuyNeural", "en-GB-RyanNeural", "en-US-AriaNeural"]
SEARCH_KEYWORDS = ["nature sunset", "ocean waves", "forest peaceful", "sky clouds"]

# Strict Visual Timeline Constants (Zero Overlap)
HOOK_DURATION = 2.0
COUNTDOWN_DURATION = 3.0  # 1 second per number (3, 2, 1)
VOICE_DELAY = HOOK_DURATION + COUNTDOWN_DURATION  # Audio & Quote start exactly at 5.0s

def safe_run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)

def get_pexels_video():
    api_key = os.getenv("PEXELS_API_KEY")
    url = f"https://api.pexels.com/videos/search?query={random.choice(SEARCH_KEYWORDS)}&orientation=portrait&per_page=5"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, headers=headers).json()
        videos = response.get("videos", [])
        if not videos: return None
        
        video_url = videos[0]["video_files"][0]["link"]
        video_path = "background_video.mp4"
        with requests.get(video_url, stream=True) as r:
            with open(video_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        return video_path
    except Exception:
        return None

async def generate_voice_with_timing(text, voice, audio_path):
    timing_data = []
    communicate = edge_tts.Communicate(text, voice)
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
    return timing_data

def generate_clean_chunks(timing_data, total_duration=None, fallback_text=None):
    """
    Groups words into tight 1-2 word phrases.
    If TTS timing fails, it auto-splits the raw text evenly so it NEVER makes a wall of text.
    """
    chunks = []
    words_per_screen = 2  # Max words on screen at once
    
    if timing_data:
        for i in range(0, len(timing_data), words_per_screen):
            group = timing_data[i : i + words_per_screen]
            phrase_text = " ".join([w["word"] for w in group]).upper()
            start_time = group[0]["start"]
            
            if i + words_per_screen < len(timing_data):
                end_time = timing_data[i + words_per_screen]["start"] - 0.02  # Tiny gap to force screen clear
            else:
                end_time = group[-1]["start"] + group[-1]["duration"]
                
            chunks.append({"text": phrase_text, "start": start_time, "end": end_time})
    elif fallback_text:
        # Fallback mechanical layout if API timing misses
        words = fallback_text.split()
        raw_chunks = [" ".join(words[i : i + words_per_screen]).upper() for i in range(0, len(words), words_per_screen)]
        per_chunk_playback = (total_duration - VOICE_DELAY - 2) / max(len(raw_chunks), 1)
        
        for idx, text_block in enumerate(raw_chunks):
            start = (idx * per_chunk_playback)
            end = start + per_chunk_playback - 0.02
            chunks.append({"text": text_block, "start": start, "end": end})
            
    return chunks

def create_youtube_short(quote, author, image_path):
    selected_voice = random.choice(VOICES)
    audio_path = "quote_audio.mp3"
    tts_text = f"{quote}"
    
    # 1. Audio Generation
    try:
        timing_data = safe_run_async(generate_voice_with_timing(tts_text, selected_voice, audio_path))
        voice_audio = AudioFileClip(audio_path)
        voice_duration = voice_audio.duration
        final_voice = voice_audio.with_start(VOICE_DELAY)
    except Exception:
        timing_data = []
        voice_duration = 12.0  # Estimated fallback math
        final_voice = AudioClip(make_frame=lambda t: np.zeros((2,)), duration=30, fps=44100)

    duration = VOICE_DELAY + voice_duration + 2.5
    
    # 2. Background Handling
    bg_video_path = get_pexels_video()
    if bg_video_path:
        bg_video = VideoFileClip(bg_video_path)
        if bg_video.duration < duration:
            bg_video = concatenate_videoclips([bg_video] * (int(duration / bg_video.duration) + 1))
        bg_video = bg_video.subclipped(0, duration).resized(height=1920)
        bg_video = bg_video.cropped(x1=(bg_video.w/2)-540, x2=(bg_video.w/2)+540, y1=0, y2=1920)
        overlay = ColorClip(size=(1080, 1920), color=[0, 0, 0], duration=duration).with_opacity(0.4)
        video = CompositeVideoClip([bg_video, overlay])
    else:
        img = Image.open(image_path).resize((1080, 1920))
        img.save("vertical_fallback.png")
        video = ImageClip("vertical_fallback.png", duration=duration)

    # 3. Audio Mix
    try:
        music = AudioFileClip(random.choice(MUSIC_FILES)).subclipped(0, duration).with_effects([MultiplyVolume(0.12)])
        video = video.with_audio(CompositeAudioClip([music, final_voice]))
    except Exception:
        video = video.with_audio(final_voice)

    # 4. Zero-Overlap Text Timeline Construction
    clips = [video]

    # Phase 1: Only the Hook Shows (0.0s - 2.0s)
    hook_clip = TextClip(
        text="READ THIS SLOWLY...", font_size=55, color="#FFD700", font="LiberationSans-Bold",
        method="caption", size=(800, None), text_align="center", stroke_color="black", stroke_width=4
    ).with_position(("center", "center")).with_start(0).with_duration(HOOK_DURATION)
    clips.append(hook_clip)

    # Phase 2: Only the Countdown Shows (2.0s - 5.0s)
    for i, num in enumerate(["3", "2", "1"]):
        num_clip = TextClip(
            text=num, font_size=180, color="#FFFFFF", font="LiberationSans-Bold",
            method="label", stroke_color="black", stroke_width=6
        ).with_position(("center", "center")).with_start(HOOK_DURATION + i).with_duration(0.95)
        clips.append(num_clip)

    # Phase 3: Flash Karaoke Popups (Starts exactly at 5.0s)
    chunks = generate_clean_chunks(timing_data, total_duration=duration, fallback_text=quote)
    for chunk in chunks:
        chunk_start = chunk["start"] + VOICE_DELAY
        chunk_end = chunk["end"] + VOICE_DELAY
        
        if chunk_start >= duration: break

        word_clip = TextClip(
            text=chunk["text"], font_size=85, color="#FFFFFF", font="LiberationSans-Bold",
            method="caption", size=(900, None), text_align="center", stroke_color="black", stroke_width=5
        ).with_position(("center", "center")).with_start(chunk_start).with_duration(chunk_end - chunk_start)
        clips.append(word_clip)

    # Phase 4: Author Outro (Only shows up AFTER the voice finishes speaking)
    outro_start = VOICE_DELAY + voice_duration
    outro_clip = TextClip(
        text=f"— {author.upper()} —\n\nSUBSCRIBE FOR MORE", font_size=45, color="#FFD700", font="LiberationSans-Bold",
        method="caption", size=(850, None), text_align="center", stroke_color="black", stroke_width=3
    ).with_position(("center", "center")).with_start(outro_start).with_duration(duration - outro_start)
    clips.append(outro_clip)

    # Render
    output_path = "clean_shorts_output.mp4"
    final_video = CompositeVideoClip(clips)
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    # Clean cache
    for f in [audio_path, "background_video.mp4", "vertical_fallback.png"]:
        if os.path.exists(f): os.remove(f)

    return output_path
