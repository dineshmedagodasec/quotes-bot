from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
import textwrap
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

def get_background():
    key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?query=nature,sunset,motivation&client_id={key}"
    res = requests.get(url).json()
    img_url = res['urls']['regular']
    img_data = requests.get(img_url).content
    return Image.open(BytesIO(img_data)).resize((1080, 1080))

def create_quote_image(quote, author):
    bg = get_background()

    # Darken background
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 140))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay)

    draw = ImageDraw.Draw(bg)

    # Load fonts
    quote_font = ImageFont.truetype("assets/fonts/font.ttf", 55)
    author_font = ImageFont.truetype("assets/fonts/font.ttf", 35)

    # Wrap text
    wrapped = textwrap.fill(f'"{quote}"', width=30)

    # Draw quote
    draw.text((540, 460), wrapped, font=quote_font,
              fill="white", anchor="mm", align="center")

    # Draw author
    draw.text((540, 700), f"— {author}", font=author_font,
              fill="#FFD700", anchor="mm")

    # Save image
    output_path = "output_quote.png"
    bg.convert("RGB").save(output_path)
    return output_path