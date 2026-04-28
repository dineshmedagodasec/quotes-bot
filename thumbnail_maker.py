from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
import textwrap
from io import BytesIO
import os
import random

# Thumbnail color schemes
COLOR_SCHEMES = [
    {"bg": "#000000", "accent": "#FF0000", "text": "#FFFFFF"},  # Black & Red
    {"bg": "#0A0F1E", "accent": "#FFD700", "text": "#FFFFFF"},  # Dark Blue & Gold
    {"bg": "#1A0A0A", "accent": "#FF6B35", "text": "#FFFFFF"},  # Dark & Orange
    {"bg": "#0A1A0F", "accent": "#00FF88", "text": "#FFFFFF"},  # Dark Green & Mint
    {"bg": "#0F0A1E", "accent": "#B388FF", "text": "#FFFFFF"},  # Dark Purple & Light Purple
    {"bg": "#1A1A1A", "accent": "#00BFFF", "text": "#FFFFFF"},  # Charcoal & Blue
    {"bg": "#000000", "accent": "#FF69B4", "text": "#FFFFFF"},  # Black & Pink
]

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_background_image():
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?query=nature,sunset,motivation&orientation=landscape&client_id={key}"
    try:
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        img_data = requests.get(img_url).content
        return Image.open(BytesIO(img_data)).resize((1280, 720))
    except:
        return None

def create_thumbnail(quote, author):
    # Pick random color scheme
    scheme = random.choice(COLOR_SCHEMES)
    bg_color = hex_to_rgb(scheme["bg"])
    accent_color = hex_to_rgb(scheme["accent"])
    text_color = hex_to_rgb(scheme["text"])

    # Try to get background image
    bg_img = get_background_image()

    if bg_img:
        # Use photo background with dark overlay
        img = bg_img.convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 180))
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        # Use solid color background
        img = Image.new("RGB", (1280, 720), bg_color)

    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        font_large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_medium = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Add left accent bar
    draw.rectangle([0, 0, 12, 720], fill=accent_color)

    # Wrap quote text
    wrapped = textwrap.fill(f'"{quote}"', width=32)
    lines = wrapped.split('\n')

    # Calculate text position
    total_height = len(lines) * 85
    start_y = (720 - total_height) // 2 - 40

    # Draw quote shadow
    for i, line in enumerate(lines):
        y = start_y + i * 85
        # Shadow
        draw.text((82, y + 3), line, font=font_large,
                  fill=(0, 0, 0))
        # Main text
        draw.text((80, y), line, font=font_large,
                  fill=text_color)

    # Draw author name in accent color
    author_y = start_y + len(lines) * 85 + 20
    draw.text((82, author_y + 2), f"— {author}",
              font=font_medium, fill=(0, 0, 0))
    draw.text((80, author_y), f"— {author}",
              font=font_medium, fill=accent_color)

    # Add channel name at bottom
    channel_text = "Daily Dose of Motivation"
    draw.text((82, 665), channel_text,
              font=font_small, fill=accent_color)

    # Add subtle gradient overlay at bottom
    for i in range(100):
        alpha = int(i * 1.5)
        draw.rectangle(
            [0, 720 - 100 + i, 1280, 720 - 99 + i],
            fill=(0, 0, 0)
        )

    # Save thumbnail
    thumbnail_path = "thumbnail.jpg"
    img.convert("RGB").save(thumbnail_path, "JPEG", quality=95)
    print(f"✅ Thumbnail created!")
    return thumbnail_path
