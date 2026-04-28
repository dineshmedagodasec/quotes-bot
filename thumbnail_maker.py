from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
import textwrap
from io import BytesIO
import os
import random

# Eye catching gradient color schemes
COLOR_SCHEMES = [
    {"bg1": (255, 0, 0), "bg2": (139, 0, 0), "accent": (255, 215, 0), "text": (255, 255, 255)},
    {"bg1": (0, 0, 139), "bg2": (0, 0, 50), "accent": (0, 255, 255), "text": (255, 255, 255)},
    {"bg1": (148, 0, 211), "bg2": (50, 0, 80), "accent": (255, 215, 0), "text": (255, 255, 255)},
    {"bg1": (255, 140, 0), "bg2": (139, 69, 0), "accent": (255, 255, 255), "text": (255, 255, 255)},
    {"bg1": (0, 128, 0), "bg2": (0, 50, 0), "accent": (255, 215, 0), "text": (255, 255, 255)},
    {"bg1": (220, 20, 60), "bg2": (100, 0, 30), "accent": (255, 255, 255), "text": (255, 255, 255)},
    {"bg1": (0, 139, 139), "bg2": (0, 50, 50), "accent": (255, 215, 0), "text": (255, 255, 255)},
]

def create_gradient(img, color1, color2):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def create_thumbnail(quote, author):
    scheme = random.choice(COLOR_SCHEMES)

    # Create 1280x720 thumbnail
    img = Image.new("RGB", (1280, 720))

    # Add gradient background
    img = create_gradient(img, scheme["bg1"], scheme["bg2"])
    draw = ImageDraw.Draw(img)

    # Add decorative elements
    # Top accent bar
    draw.rectangle([0, 0, 1280, 12], fill=scheme["accent"])
    # Bottom accent bar
    draw.rectangle([0, 708, 1280, 720], fill=scheme["accent"])
    # Left accent bar
    draw.rectangle([0, 0, 12, 720], fill=scheme["accent"])
    # Right accent bar
    draw.rectangle([1268, 0, 1280, 720], fill=scheme["accent"])

    # Add diagonal decorative lines
    for i in range(0, 1280, 80):
        draw.line([(i, 0), (i + 40, 720)], fill=(255, 255, 255, 30), width=1)

    # Load fonts
    try:
        font_huge = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
        font_medium = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
        font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_huge = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Wrap quote text
    wrapped = textwrap.fill(quote, width=28)
    lines = wrapped.split('\n')

    # Choose font size based on line count
    if len(lines) <= 2:
        font = font_huge
        line_height = 95
    elif len(lines) <= 3:
        font = font_large
        line_height = 80
    else:
        font = font_medium
        line_height = 60

    total_height = len(lines) * line_height
    start_y = max(40, (720 - total_height - 100) // 2)

    # Draw quote shadow
    for i, line in enumerate(lines):
        y = start_y + i * line_height
        # Shadow effect
        draw.text((44, y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((42, y + 2), line, font=font, fill=(0, 0, 0))
        # Main text
        draw.text((40, y), line, font=font, fill=scheme["text"])

    # Draw divider line
    divider_y = start_y + len(lines) * line_height + 15
    draw.rectangle([40, divider_y, 400, divider_y + 4], fill=scheme["accent"])

    # Draw author name
    author_y = divider_y + 20
    draw.text((42, author_y + 3), f"— {author}", font=font_medium, fill=(0, 0, 0))
    draw.text((40, author_y), f"— {author}", font=font_medium, fill=scheme["accent"])

    # Channel name badge at bottom right
    badge_text = "Daily Dose of Motivation"
    draw.rectangle([880, 660, 1270, 705], fill=scheme["accent"])
    draw.text((895, 668), badge_text, font=font_small, fill=(0, 0, 0))

    thumbnail_path = "thumbnail.jpg"
    img.convert("RGB").save(thumbnail_path, "JPEG", quality=95)
    print("Thumbnail created!")
    return thumbnail_path
