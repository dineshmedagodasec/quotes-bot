from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap
from io import BytesIO
import os
import random

COLOR_SCHEMES = [
    {"bg": (0, 0, 0), "accent": (255, 0, 0), "text": (255, 255, 255)},
    {"bg": (10, 15, 30), "accent": (255, 215, 0), "text": (255, 255, 255)},
    {"bg": (26, 10, 10), "accent": (255, 107, 53), "text": (255, 255, 255)},
    {"bg": (10, 26, 15), "accent": (0, 255, 136), "text": (255, 255, 255)},
    {"bg": (15, 10, 30), "accent": (179, 136, 255), "text": (255, 255, 255)},
    {"bg": (26, 26, 26), "accent": (0, 191, 255), "text": (255, 255, 255)},
    {"bg": (0, 0, 0), "accent": (255, 105, 180), "text": (255, 255, 255)},
]

def get_background_image():
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?query=nature,sunset,motivation&orientation=landscape&client_id={key}"
    try:
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        img_data = requests.get(img_url).content
        return Image.open(BytesIO(img_data)).resize((1280, 720))
    except Exception as e:
        print(f"Background image failed: {e}")
        return None

def create_thumbnail(quote, author):
    scheme = random.choice(COLOR_SCHEMES)
    bg_color = scheme["bg"]
    accent_color = scheme["accent"]
    text_color = scheme["text"]

    # Try background image
    bg_img = get_background_image()
    if bg_img:
        img = bg_img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 180))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        img = Image.new("RGB", (1280, 720), bg_color)

    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_medium = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Left accent bar
    draw.rectangle([0, 0, 14, 720], fill=accent_color)

    # Wrap quote
    wrapped = textwrap.fill(f'"{quote}"', width=30)
    lines = wrapped.split('\n')

    total_height = len(lines) * 88
    start_y = max(60, (720 - total_height) // 2 - 60)

    # Draw quote text
    for i, line in enumerate(lines):
        y = start_y + i * 88
        draw.text((82, y + 3), line, font=font_large, fill=(0, 0, 0))
        draw.text((80, y), line, font=font_large, fill=text_color)

    # Draw author
    author_y = start_y + len(lines) * 88 + 20
    draw.text((82, author_y + 2), f"— {author}", font=font_medium, fill=(0, 0, 0))
    draw.text((80, author_y), f"— {author}", font=font_medium, fill=accent_color)

    # Channel name at bottom
    draw.rectangle([0, 650, 1280, 720], fill=(0, 0, 0))
    draw.text((80, 665), "Daily Dose of Motivation", font=font_small, fill=accent_color)

    thumbnail_path = "thumbnail.jpg"
    img.convert("RGB").save(thumbnail_path, "JPEG", quality=95)
    print("Thumbnail created!")
    return thumbnail_path
