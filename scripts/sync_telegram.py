import json, re, requests
from bs4 import BeautifulSoup

# Replace with any public Telegram channel username you want to test
CHANNELS = ["example_donghua_channel"]
IGNORE_RE = re.compile(r"\b(pv|teaser|trailer|preview|raw)\b", re.I)
EP_RE = re.compile(r"(?:ep|episode)\s*0*(\d+)", re.I)
LINK_RE = re.compile(r"https?://[^\s<>\"']+")

results = []
for ch in CHANNELS:
    r = requests.get(f"https://t.me/s/{ch}", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")
    for msg in soup.select(".tgme_widget_message_wrap"):
        text_el = msg.select_one(".tgme_widget_message_text")
        if not text_el:
            continue
        text = text_el.get_text(" ", strip=True)
        if IGNORE_RE.search(text):
            continue
        ep_match = EP_RE.search(text)
        if not ep_match:
            continue
        links = [a["href"] for a in text_el.select("a[href]") if "t.me" not in a["href"]]
        post_link = msg.select_one("a.tgme_widget_message_date")
        results.append({
            "channel": ch,
            "episode": int(ep_match.group(1)),
            "title": text[:120],
            "mirror_links": links,
            "telegram_post": post_link["href"] if post_link else ""
        })

with open("data/telegram_feed.json", "w", encoding="utf-8") as f:
    json.dump(results[-30:][::-1], f, indent=2, ensure_ascii=False)
print(f"Saved {len(results[-30:])} items.")
