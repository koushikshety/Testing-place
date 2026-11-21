import json
import urllib.parse
import requests

# Add any public Rumble video page URLs here to test
RUMBLE_URLS = [
    # Example: "https://rumble.com/v7gg4yg-example-video.html"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/128.0.0.0 Mobile Safari/537.36"
}

def build_catalog():
    catalog = []
    for url in RUMBLE_URLS:
        oembed_url = f"https://rumble.com/api/Media/oembed.json?url={urllib.parse.quote(url, safe='')}"
        try:
            res = requests.get(oembed_url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                data = res.json()
                catalog.append({
                    "title": data.get("title", "Untitled Rumble Video"),
                    "author": data.get("author_name", ""),
                    "thumbnail": data.get("thumbnail_url", ""),
                    "embed_html": data.get("html", ""),
                    "source_url": url
                })
                print(f"[+] Added: {data.get('title')}")
            else:
                print(f"[!] HTTP {res.status_code} for {url}")
        except Exception as e:
            print(f"[!] Error for {url}: {e}")

    with open("rumble_catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved {len(catalog)} item(s) to rumble_catalog.json")

if __name__ == "__main__":
    build_catalog()
