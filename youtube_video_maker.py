from moviepy import ImageClip, AudioFileClip, CompositeAudioClip
from PIL import Image
from gtts import gTTS
import os
import random
import requests

# 7 free royalty-free motivational music tracks from chosic.com
MUSIC_URLS = [
    "https://www.chosic.com/wp-content/uploads/2021/04/Alexander_Nakarada-Fanfare_x.mp3",
    "https://www.chosic.com/wp-content/uploads/2022/01/purrple-cat-equinox.mp3",
    "https://www.chosic.com/wp-content/uploads/2021/07/Inspiring-Cinematic-Ambient.mp3",
    "https://www.chosic.com/wp-content/uploads/2022/05/good-night.mp3",
    "https://www.chosic.com/wp-content/uploads/2021/04/scott-buckley-luminary.mp3",
    "https://www.chosic.com/wp-content/uploads/2022/03/reflection-of-you-and-me.mp3",
    "https://www.chosic.com/wp-content/uploads/2021/07/energy-by-bensound.mp3",
]

def get_random_music():
    url = random.choice(MUSIC_URLS)
    print(f"🎵 Downloading music from: {url}")
    try:
        response = requests.get(url, timeout=15)
        music_path = "background_music.mp3"
        with open(music_path, "wb") as f:
            f.write(response.content)
        return music_path
    except:
        print("⚠️ Music download failed, continuing without music")
        return None

def create_youtube_short(quote, author, image_path):
    # Generate voice audio
    tts_text = f"{quote}... by {author}"
    tts = gTTS(text=tts_text, lang='en', slow=False)
    audio_path = "quote_audio.mp3"
    tts.save(audio_path)

    # Create vertical image for Shorts
    img = Image.open(image_path)
    img_resized = img.resize((1080, 1920))
    vertical_path = "vertical_quote.png"
    img_resized.save(vertical_path)

    # Load voice audio
    voice_clip = AudioFileClip(audio_path)
    duration = min(voice_clip.duration + 2, 59)

    # Try to add background music
    music_path = get_random_music()
    if music_path and os.path.exists(music_path):
        music_clip = AudioFileClip(music_path).subclipped(0, duration)
        # Lower music volume to 15% so voice is clear
        music_clip = music_clip.with_effects([])
        music_clip = music_clip.multiply_volume(0.15)
        final_audio = CompositeAudioClip([music_clip, voice_clip])
    else:
        final_audio = voice_clip

    # Create video
    video = ImageClip(vertical_path, duration=duration)
    video = video.with_audio(final_audio)

    output_path = "youtube_short.mp4"
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    # Cleanup temp files
    for f in [audio_path, "background_music.mp3", vertical_path]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
