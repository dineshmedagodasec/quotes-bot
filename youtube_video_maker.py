from moviepy import ImageClip, AudioFileClip
from PIL import Image
from gtts import gTTS
import os
import random

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

    # Create video with voice only
    video = ImageClip(vertical_path, duration=duration)
    video = video.with_audio(voice_clip)

    output_path = "youtube_short.mp4"
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    # Cleanup temp files
    for f in [audio_path, vertical_path]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
