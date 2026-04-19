from moviepy import ImageClip, AudioFileClip
from PIL import Image
from gtts import gTTS
import os

def create_youtube_short(quote, author, image_path):
    # Generate audio from quote
    tts_text = f"{quote}... by {author}"
    tts = gTTS(text=tts_text, lang='en', slow=False)
    audio_path = "quote_audio.mp3"
    tts.save(audio_path)

    # Create vertical image for Shorts (1080x1920)
    img = Image.open(image_path)
    img_resized = img.resize((1080, 1920))
    vertical_path = "vertical_quote.png"
    img_resized.save(vertical_path)

    # Create video from image + audio
    audio_clip = AudioFileClip(audio_path)
    duration = min(audio_clip.duration + 2, 59)

    video = ImageClip(vertical_path, duration=duration)
    video = video.with_audio(audio_clip)

    output_path = "youtube_short.mp4"
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    return output_path
