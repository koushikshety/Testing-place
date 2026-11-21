import json, os, re, requests

SERIES_QUERIES = {
    "Renegade Immortal": ["Renegade Immortal", "Xian Ni", "Renegade Immortal Ep"],
    "Soul Land 2": ["Soul Land 2", "SL2"],
    "Battle Through the Heavens": ["Battle Through the Heavens", "BTTH"]
}

# Filter out trailers, reactions, and non-English sub uploads
IGNORE_RE = re.compile(
    r"\b(pv|teaser|trailer|preview|reaction|review|amv|edit|ost|song|"
    r"vostfr|vf|sub[\s._-]?indo|indo|indonesian|sub[\s._-]?es|esp|espanol|"
    r"pt[\s._-]?br|portugues|sub[\s._-]?th|thai|viet|vietsub|rus|arabic)\b",
    re.I
)
EXPLICIT_EP_RE = re.compile(r"(?:ep|episode|part)[\s._-]*0*(\d{1,4})\b", re.I)
SHORTHAND_EP_RE = re.compile(r"\b(?:SL2|RI|BTTH|XN)[\s._-]*0*(\d{1,4})\b", re.I)
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUT_FILE = "data/embeds.json"

results = []
if os.path.exists(OUT_FILE):
    try:
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception:
        results = []

# Clean previously saved non-English items too
results = [r for r in results if not IGNORE_RE.search(r.get("title", ""))]
seen = {item.get("url") for item in results if item.get("url")}
added = 0

for series, queries in SERIES_QUERIES.items():
    for q in queries:
        for offset in (0, 50):
            try:
                r = requests.get(
                    "https://lighthouse.odysee.tv/search",
                    params={"s": q, "size": 50, "from": offset, "mediaType": "video"},
                    headers=HEADERS,
                    timeout=15
                )
                items = r.json() if r.status_code == 200 else []
                if not items:
                    break

                for item in items:
                    claim_id = item.get("claimId", "")
                    name = item.get("name", "")
                    title = (item.get("title") or name).strip()

                    if not claim_id or not name or title.isdigit() or IGNORE_RE.search(title):
                        continue

                    ep_match = EXPLICIT_EP_RE.search(title) or SHORTHAND_EP_RE.search(title)
                    if not ep_match:
                        continue

                    ep_num = int(ep_match.group(1))
                    if ep_num <= 0 or ep_num > 1000:
                        continue

                    embed_url = f"https://odysee.com/$/embed/{name}/{claim_id}"
                    if embed_url in seen:
                        continue
                    seen.add(embed_url)

                    results.append({
                        "series": series,
                        "episode": ep_num,
                        "title": title[:120],
                        "server": "Odysee",
                        "type": "iframe",
                        "url": embed_url
                    })
                    added += 1
            except Exception as e:
                print(f"[{q} @{offset}] Error: {e}")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Added {added} clean English embeds. Total saved: {len(results)}")
