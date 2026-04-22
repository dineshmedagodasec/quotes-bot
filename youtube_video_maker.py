from moviepy import ImageClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx import MultiplyVolume
from PIL import Image
from gtts import gTTS
import os
import random

MUSIC_FILES = [
    "music/music_1.mp3",
    "music/music_2.mp3",
    "music/music_3.mp3",
    "music/music_4.mp3",
    "music/music_5.mp3",
    "music/music_6.mp3",
    "music/music_7.mp3",
]

def create_youtube_short(quote, author, image_path):
    # Step 1: Generate voice audio
    tts_text = f"{quote}... by {author}"
    tts = gTTS(text=tts_text, lang='en', slow=False)
    audio_path = "quote_audio.mp3"
    tts.save(audio_path)

    # Step 2: Create vertical image for Shorts
    img = Image.open(image_path)
    img_resized = img.resize((1080, 1920))
    vertical_path = "vertical_quote.png"
    img_resized.save(vertical_path)

    # Step 3: Load voice audio
    voice_clip = AudioFileClip(audio_path)
    duration = min(voice_clip.duration + 2, 59)

    # Step 4: Pick random music track
    music_file = random.choice(MUSIC_FILES)
    print(f"🎵 Using music: {music_file}")

    try:
        music_clip = AudioFileClip(music_file)
        music_clip = music_clip.subclipped(0, duration)
        # Fix: Use MultiplyVolume effect instead
        music_clip = music_clip.with_effects([MultiplyVolume(0.15)])
        final_audio = CompositeAudioClip([music_clip, voice_clip])
    except Exception as e:
        print(f"⚠️ Music failed: {e} — using voice only")
        final_audio = voice_clip

    # Step 5: Create video
    video = ImageClip(vertical_path, duration=duration)
    video = video.with_audio(final_audio)

    output_path = "youtube_short.mp4"
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    # Step 6: Cleanup
    for f in [audio_path, vertical_path]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
