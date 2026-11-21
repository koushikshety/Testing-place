import json, os, requests, xml.etree.ElementTree as ET

RSS_URL = os.getenv("TEST_RSS_URL", "")
API_KEY = os.getenv("HOST_API_KEY", "")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
KEYWORDS = ["renegade immortal", "xian ni", "soul land", "jade dynasty"]

if not RSS_URL:
    print("Set TEST_RSS_URL to test.")
    raise SystemExit(0)

xml_text = requests.get(RSS_URL, timeout=15).text
root = ET.fromstring(xml_text)

with open("data/remote_uploads.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)
seen = {item["source_link"] for item in catalog}

for item in root.findall(".//item")[:25]:
    title = item.findtext("title", "")
    link = item.findtext("link", "")
    if link in seen or not any(k in title.lower() for k in KEYWORDS):
        continue

    embed_url = ""
    if not DRY_RUN and API_KEY:
        # Generic remote-upload pattern (adjust endpoint/params to match your chosen host's docs)
        resp = requests.get(
            "https://api.examplehost.com/api/upload/url",
            params={"key": API_KEY, "url": link},
            timeout=20
        ).json()
        file_code = resp.get("result", {}).get("filecode", "")
        embed_url = f"https://examplehost.com/e/{file_code}" if file_code else ""

    catalog.insert(0, {"title": title, "source_link": link, "embed_url": embed_url, "dry_run": DRY_RUN})
    seen.add(link)

with open("data/remote_uploads.json", "w", encoding="utf-8") as f:
    json.dump(catalog[:30], f, indent=2)
print(f"Catalog now has {len(catalog[:30])} entries (DRY_RUN={DRY_RUN}).")
