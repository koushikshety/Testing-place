import json, os, re, requests
import xml.etree.ElementTree as ET

RSS_URL = os.getenv("TEST_RSS_URL", "").strip()
API_KEY = os.getenv("HOST_API_KEY", "").strip()
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
OUT_FILE = "data/remote_uploads.json"
EP_RE = re.compile(r"(?:ep|episode|\be|-)\s*0*(\d{1,4})\b", re.I)

if not RSS_URL:
    print("Set TEST_RSS_URL to test.")
    raise SystemExit(0)

existing = []
if os.path.exists(OUT_FILE):
    try:
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception:
        existing = []

seen_sources = {item.get("source_url") for item in existing}

r = requests.get(RSS_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
root = ET.fromstring(r.text)

added = 0
for item in root.findall(".//item")[:5]:
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    if not title or not link or link in seen_sources:
        continue

    ep_match = EP_RE.search(title)
    ep_num = int(ep_match.group(1)) if ep_match else 0

    if DRY_RUN or not API_KEY:
        existing.insert(0, {
            "series": "Renegade Immortal",
            "episode": ep_num,
            "title": f"{title[:110]} (Dry Run)",
            "server": "FileMoon",
            "type": "iframe",
            "url": "",
            "source_url": link
        })
        seen_sources.add(link)
        added += 1
        continue

    if added >= 2:
        break

    try:
        resp = requests.post(
            "https://filemoon.org/api/v1/remote-uploads",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            json={"url": link, "urls": [link]},
            timeout=20
        )
        print(f"[FileMoon] HTTP {resp.status_code} | {resp.text[:250]}")
        data = resp.json() if resp.text.strip().startswith("{") else {}
        jobs = data.get("data") or []
        job = jobs[0] if isinstance(jobs, list) and jobs else (jobs if isinstance(jobs, dict) else {})
        file_id = job.get("file_id") or job.get("id") or ""

        if resp.status_code in (200, 201, 202) and file_id:
            existing.insert(0, {
                "series": "Renegade Immortal",
                "episode": ep_num,
                "title": title[:110],
                "server": "FileMoon",
                "type": "iframe",
                "url": f"https://filemoon.org/e/{file_id}",
                "source_url": link
            })
            seen_sources.add(link)
            added += 1
    except Exception as e:
        print(f"[FileMoon] Error: {e}")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(existing[:50], f, indent=2, ensure_ascii=False)

print(f"Done. Added {added} items. Total in {OUT_FILE}: {len(existing[:50])}")
