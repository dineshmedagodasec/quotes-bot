import requests
import os
import json
import base64
import random

# Backup quotes if API fails or rate limited
BACKUP_QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("Success is not final failure is not fatal. It is the courage to continue that counts.", "Winston Churchill"),
    ("Believe you can and you are halfway there.", "Theodore Roosevelt"),
    ("You miss 100% of the shots you do not take.", "Wayne Gretzky"),
    ("Whether you think you can or you think you cannot you are right.", "Henry Ford"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Spread love everywhere you go.", "Mother Teresa"),
    ("You will face many defeats in life but never let yourself be defeated.", "Maya Angelou"),
    ("The greatest glory in living lies not in never falling but in rising every time we fall.", "Nelson Mandela"),
    ("Never let the fear of striking out keep you from playing the game.", "Babe Ruth"),
    ("Life is either a daring adventure or nothing at all.", "Helen Keller"),
    ("What you get by achieving your goals is not as important as what you become.", "Thoreau"),
    ("Hardships often prepare ordinary people for an extraordinary destiny.", "C.S. Lewis"),
    ("You are never too old to set another goal or to dream a new dream.", "C.S. Lewis"),
    ("To handle yourself use your head to handle others use your heart.", "Eleanor Roosevelt"),
    ("Too many of us are not living our dreams because we are living our fears.", "Les Brown"),
    ("Do what you can with all you have wherever you are.", "Theodore Roosevelt"),
]

# Error messages to detect and reject
ERROR_MESSAGES = [
    "too many requests",
    "obtain an auth key",
    "rate limit",
    "zenquotes.io",
    "error",
    "unauthorized",
    "blocked",
    "invalid",
]

def is_error_message(quote):
    quote_lower = quote.lower()
    return any(error in quote_lower for error in ERROR_MESSAGES)

def get_used_quotes():
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO_NAME", "dineshmedagodasec/quotes-bot")
    url = f"https://api.github.com/repos/{repo_name}/contents/used_quotes.json"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json().get("content", "")
            decoded = base64.b64decode(content).decode()
            return json.loads(decoded)
    except:
        pass
    return []

def save_used_quote(quote):
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("REPO_NAME", "dineshmedagodasec/quotes-bot")
    url = f"https://api.github.com/repos/{repo_name}/contents/used_quotes.json"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        used = get_used_quotes()
        used.append(quote[:50])
        if len(used) > 500:
            used = used[-500:]
        content = json.dumps(used)
        encoded = base64.b64encode(content.encode()).decode()
        sha = None
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json().get("sha")
        data = {
            "message": "Update used quotes",
            "content": encoded
        }
        if sha:
            data["sha"] = sha
        requests.put(url, headers=headers, json=data)
        print(f"Saved quote: {quote[:30]}")
    except Exception as e:
        print(f"Save quote failed: {e}")

def get_quote():
    used_quotes = get_used_quotes()
    print(f"Used quotes so far: {len(used_quotes)}")

    # Try API 3 times
    for attempt in range(3):
        try:
            url = "https://zenquotes.io/api/random"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                quote = data[0]['q']
                author = data[0]['a']

                # Reject error messages
                if is_error_message(quote):
                    print(f"API rate limited - using backup quote")
                    break

                # Check duplicate
                quote_key = quote[:50]
                if quote_key not in used_quotes:
                    print(f"New quote found!")
                    save_used_quote(quote)
                    return quote, author
                else:
                    print(f"Duplicate found attempt {attempt + 1}")

        except Exception as e:
            print(f"API failed: {e}")

    # Use backup quotes
    print("Using backup quote!")
    random.shuffle(BACKUP_QUOTES)
    for backup_quote, backup_author in BACKUP_QUOTES:
        quote_key = backup_quote[:50]
        if quote_key not in used_quotes:
            save_used_quote(backup_quote)
            return backup_quote, backup_author

    # Last resort
    backup = random.choice(BACKUP_QUOTES)
    return backup[0], backup[1]
