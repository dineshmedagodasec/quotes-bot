from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip
from moviepy.audio.fx import MultiplyVolume
from PIL import Image
from gtts import gTTS
import os
import random
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
    duration = max(voice_clip.duration + 2, 30)
    duration = min(duration, 59)

    # Step 4: Pick random music track
    music_file = random.choice(MUSIC_FILES)
    print(f"Music: {music_file}")

    try:
        music_clip = AudioFileClip(music_file)
        music_clip = music_clip.subclipped(0, duration)
        music_clip = music_clip.with_effects([MultiplyVolume(0.15)])
        final_audio = CompositeAudioClip([music_clip, voice_clip])
    except Exception as e:
        print(f"Music failed: {e}")
        final_audio = voice_clip

    # Step 5: Create base video
    video = ImageClip(vertical_path, duration=duration)
    video = video.with_audio(final_audio)

    # Step 6: Add text overlays
    try:
        wrapped_quote = textwrap.fill(quote, width=35)
        quote_text = f'"{wrapped_quote}"'

        quote_clip = TextClip(
            text=quote_text,
            font_size=60,
            color="white",
            font="DejaVuSans-Bold",
            method="caption",
            size=(900, None),
            text_align="center"
        )
        quote_clip = quote_clip.with_position(
            lambda t: ("center", max(600, 800 - int(t * 100)))
            if t < 2 else ("center", 600)
        )
        quote_clip = quote_clip.with_start(1)
        quote_clip = quote_clip.with_duration(duration - 1)

        author_clip = TextClip(
            text=f"— {author}",
            font_size=40,
            color="#FFD700",
            font="DejaVuSans",
            method="label",
            text_align="center"
        )
        author_clip = author_clip.with_position(
            lambda t: ("center", max(900, 1100 - int(t * 100)))
            if t < 2 else ("center", 900)
        )
        author_clip = author_clip.with_start(3)
        author_clip = author_clip.with_duration(duration - 3)

        channel_clip = TextClip(
            text="Follow for daily motivation!",
            font_size=32,
            color="white",
            font="DejaVuSans",
            method="label",
            text_align="center"
        )
        channel_clip = channel_clip.with_position(("center", 1800))
        channel_clip = channel_clip.with_start(0)
        channel_clip = channel_clip.with_duration(duration)

        final_video = CompositeVideoClip([
            video,
            quote_clip,
            author_clip,
            channel_clip
        ])
        print("Text animations added!")

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

    for f in [audio_path, vertical_path]:
        if os.path.exists(f):
            os.remove(f)

    return output_path
