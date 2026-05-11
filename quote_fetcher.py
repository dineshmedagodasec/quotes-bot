import requests
import os
import json
import base64

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
        # Get existing quotes
        used = get_used_quotes()

        # Add new quote
        used.append(quote[:50])

        # Keep only last 500 quotes
        if len(used) > 500:
            used = used[-500:]

        content = json.dumps(used)
        encoded = base64.b64encode(content.encode()).decode()

        # Get SHA if file exists
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
        print(f"Saved used quote: {quote[:30]}")

    except Exception as e:
        print(f"Save quote failed: {e}")

def get_quote():
    used_quotes = get_used_quotes()
    print(f"Used quotes so far: {len(used_quotes)}")

    # Try up to 10 times to get a unique quote
    for attempt in range(10):
        try:
            url = "https://zenquotes.io/api/random"
            response = requests.get(url)
            data = response.json()
            quote = data[0]['q']
            author = data[0]['a']

            # Check if quote was used before
            quote_key = quote[:50]
            if quote_key not in used_quotes:
                print(f"New quote found on attempt {attempt + 1}")
                save_used_quote(quote)
                return quote, author
            else:
                print(f"Duplicate found attempt {attempt + 1} trying again...")

        except Exception as e:
            print(f"Quote fetch failed: {e}")

    # If all attempts fail return last fetched quote
    print("Could not find unique quote after 10 attempts using last one")
    return quote, author
