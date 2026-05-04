import requests
import os

def format_caption(quote, author):
    # Format caption with proper line breaks for Facebook
    lines = quote.split('\n')
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if line:
            formatted_lines.append(line)
        else:
            formatted_lines.append('')

    formatted_quote = '\n'.join(formatted_lines)

    caption = f'{formatted_quote}\n\n— {author}\n\n💪 Follow for daily motivation!\n\n#Motivation #Quotes #DailyQuote #Inspiration #MindsetMatters #SuccessQuotes #PositiveVibes'

    return caption

def post_to_facebook(image_path, quote, author):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    album_id = os.getenv("FACEBOOK_ALBUM_ID")

    caption = format_caption(quote, author)

    with open(image_path, "rb") as img:
        upload_url = f"https://graph.facebook.com/{album_id}/photos"
        response = requests.post(upload_url, data={
            "caption": caption,
            "access_token": token,
            "published": "true"
        }, files={"source": img})

    result = response.json()
    print("Posted successfully:", result)
    return result
