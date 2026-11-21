import base64
import json
import time
from bs4 import BeautifulSoup
import requests

SOURCE_URL = "https://donghuastream.org/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 14; iQOO Neo 10) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def extract_rumble_embed(ep_url):
    try:
        res = requests.get(ep_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for opt in soup.select("select.mirror option"):
            val = opt.get("value", "").strip()
            if not val:
                continue
            decoded = base64.b64decode(val).decode("utf-8", errors="ignore")
            iframe = BeautifulSoup(decoded, "html.parser").find("iframe")
            if iframe and iframe.get("src"):
                src = iframe["src"]
                if src.startswith("//"):
                    src = "https:" + src
                if "rumble.com/embed/" in src.lower():
                    return src
    except Exception:
        pass
    return None

def sync():
    res = requests.get(SOURCE_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    catalog = []
    seen_urls = set()

    for card in soup.select("article.bs a")[:12]:
        ep_url = card.get("href")
        title = (card.get("title") or card.text).strip()
        if not ep_url or ep_url in seen_urls:
            continue
        seen_urls.add(ep_url)

        rumble_url = extract_rumble_embed(ep_url)
        if rumble_url:
            catalog.append({
                "title": title,
                "category": "donghua",
                "embed_url": rumble_url
            })
            print(f"[+] Added Rumble: {title}")
        time.sleep(0.5)

    with open("rumble_catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved {len(catalog)} Rumble episodes to rumble_catalog.json")

if __name__ == "__main__":
    sync()
