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

# Animation styles
ANIMATIONS = ["slide_up", "slide_down", "slide_left", "slide_right", "zoom_in", "bounce", "pop"]

def get_position(animation, t, base_x, base_y, video_width=1080, video_height=1920):
    if animation == "slide_up":
        y = max(base_y, base_y + 200 - int(t * 150)) if t < 1.5 else base_y
        return ("center", y)
    elif animation == "slide_down":
        y = max(base_y, base_y - 200 + int(t * 150)) if t < 1.5 else base_y
        return ("center", y)
    elif animation == "slide_left":
        x = max(0, video_width - int(t * 800)) if t < 1.5 else "center"
        return (x, base_y)
    elif animation == "slide_right":
        x = min(video_width, int(t * 800) - video_width) if t < 1.5 else "center"
        return (x, base_y)
    elif animation == "bounce":
        if t < 0.3:
            y = base_y - int(t * 400)
        elif t < 0.6:
            y = base_y - 120 + int((t - 0.3) * 400)
        elif t < 0.8:
            y = base_y + int((t - 0.6) * 200)
        elif t < 1.0:
            y = base_y + 40 - int((t - 0.8) * 200)
        else:
            y = base_y
        return ("center", y)
    elif animation == "zoom_in":
        return ("center", base_y)
    elif animation == "pop":
        return ("center", base_y)
    else:
        return ("center", base_y)

def apply_animation(clip, animation, base_y):
    if animation in ["slide_up", "slide_down", "bounce"]:
        clip = clip.with_position(lambda t: get_position(animation, t, "center", base_y))
    elif animation == "slide_left":
        clip = clip.with_position(lambda t: get_position(animation, t, "center", base_y))
    elif animation == "slide_right":
        clip = clip.with_position(lambda t: get_position(animation, t, "center", base_y))
    elif animation == "zoom_in":
        clip = clip.with_position(("center", base_y))
    elif animation == "pop":
        clip = clip.with_position(("center", base_y))
    else:
        clip = clip.with_position(("center", base_y))
    return clip

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

    # Step 6: Pick random animation
    animation = random.choice(ANIMATIONS)
    print(f"Animation: {animation}")

    # Step 7: Add text overlays
    try:
        wrapped_quote = textwrap.fill(quote, width=30)
        quote_text = f'"{wrapped_quote}"\n\n'

        # Quote text
        quote_clip = TextClip(
            text=quote_text,
            font_size=60,
            color="white",
            font="LiberationSans-Bold",
            method="caption",
            size=(820, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        quote_clip = apply_animation(quote_clip, animation, 500)
        quote_clip = quote_clip.with_start(1)
        quote_clip = quote_clip.with_duration(duration - 1)

        # Author text
        author_clip = TextClip(
            text=f"— {author}\n\n",
            font_size=34,
            color="#FFD700",
            font="DejaVuSans",
            method="caption",
            size=(780, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        author_clip = apply_animation(author_clip, animation, 1200)
        author_clip = author_clip.with_start(3)
        author_clip = author_clip.with_duration(duration - 3)

        # Channel watermark
        channel_clip = TextClip(
            text="Follow for daily motivation!",
            font_size=28,
            color="white",
            font="DejaVuSans",
            method="caption",
            size=(780, None),
            text_align="center",
            stroke_color="black",
            stroke_width=1
        )
        channel_clip = channel_clip.with_position(("center", 1780))
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
        print(f"Text animation failed: {e} — using plain video")
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
