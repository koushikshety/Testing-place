import json, re, requests

QUERIES = [
    "Renegade Immortal",
    "Soul Land 2",
    "Battle Through the Heavens"
]
IGNORE_RE = re.compile(r"\b(pv|teaser|trailer|preview|reaction|review|amv|edit)\b", re.I)
EXPLICIT_EP_RE = re.compile(r"(?:ep|episode|part)[\s._-]*0*(\d{1,4})\b", re.I)
SHORTHAND_EP_RE = re.compile(r"\b(?:SL2|RI|BTTH)[\s._-]*0*(\d{1,4})\b", re.I)
HEADERS = {"User-Agent": "Mozilla/5.0"}

results = []
seen = set()

for q in QUERIES:
    try:
        r = requests.get(
            "https://lighthouse.odysee.tv/search",
            params={"s": q, "size": 15, "from": 0, "mediaType": "video"},
            headers=HEADERS,
            timeout=15
        )
        items = r.json() if r.status_code == 200 else []
        print(f"[{q}] HTTP {r.status_code} | candidates: {len(items)}")

        for item in items:
            claim_id = item.get("claimId", "")
            name = item.get("name", "")
            title = (item.get("title") or name).strip()

            # Skip blank, purely numeric, or non-episode titles
            if not claim_id or not name or title.isdigit() or IGNORE_RE.search(title):
                continue

            ep_match = EXPLICIT_EP_RE.search(title) or SHORTHAND_EP_RE.search(title)
            if not ep_match:
                continue

            embed_url = f"https://odysee.com/$/embed/{name}/{claim_id}"
            if embed_url in seen:
                continue
            seen.add(embed_url)

            results.append({
                "series": q,
                "episode": int(ep_match.group(1)),
                "title": title[:120],
                "server": "Odysee",
                "type": "iframe",
                "url": embed_url
            })
    except Exception as e:
        print(f"[{q}] Error: {e}")

with open("data/embeds.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Saved {len(results)} clean embeds to data/embeds.json")
