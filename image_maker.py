from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap
from io import BytesIO
import os

def get_background():
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?query=nature,sunset,motivation&orientation=squarish&client_id={key}"
    res = requests.get(url).json()
    img_url = res['urls']['regular']
    img_data = requests.get(img_url).content
    return Image.open(BytesIO(img_data)).resize((1080, 1080))

def create_quote_image(quote, author):
    # Get background
    bg = get_background()

    # Dark overlay
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 160))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay)

    # Save clean background for YouTube
    clean_path = "output_quote_clean.png"
    bg.convert("RGB").save(clean_path)

    # Add text for Facebook version
    draw = ImageDraw.Draw(bg)

    try:
        quote_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 52)
        author_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36)
    except:
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Wrap and draw quote
    wrapped = textwrap.fill(f'"{quote}"', width=28)
    draw.multiline_text(
        (540, 420),
        wrapped,
        font=quote_font,
        fill="white",
        anchor="mm",
        align="center",
        spacing=12
    )

    # Draw author
    draw.text(
        (540, 680),
        f"— {author}",
        font=author_font,
        fill="#FFD700",
        anchor="mm"
    )

    # Draw watermark
    draw.text(
        (540, 980),
        "Daily Dose of Motivation",
        font=author_font,
        fill=(255, 255, 255, 180),
        anchor="mm"
    )

    # Save Facebook version with text
    fb_path = "output_quote.png"
    bg.convert("RGB").save(fb_path)

    return fb_path, clean_path
