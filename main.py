from dotenv import load_dotenv
from quote_fetcher import get_quote
from image_maker import create_quote_image
from facebook_poster import post_to_facebook

load_dotenv()

def run_bot():
    print("🔍 Fetching quote...")
    quote, author = get_quote()
    print(f"✅ Quote: {quote} — {author}")

    print("🎨 Creating image...")
    image_path = create_quote_image(quote, author)
    print("✅ Image created!")

    print("📤 Posting to Facebook...")
    result = post_to_facebook(image_path, quote, author)
    print("✅ Done! Post published.")

if __name__ == "__main__":
    run_bot()