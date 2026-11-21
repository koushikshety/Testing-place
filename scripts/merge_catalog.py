import json, os

def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

embeds = load_json("data/embeds.json")
remotes = load_json("data/remote_uploads.json")

catalog_map = {}

for item in remotes + embeds:
    url = (item.get("url") or "").strip()
    if not url:
        continue
    series = item.get("series") or "Donghua"
    ep = int(item.get("episode") or 0)
    key = f"{series.lower()}::{ep}"

    if key not in catalog_map:
        catalog_map[key] = {
            "series": series,
            "episode": ep,
            "title": item.get("title") or f"{series} Episode {ep}",
            "servers": []
        }

    # Avoid duplicate URLs
    if not any(s["url"] == url for s in catalog_map[key]["servers"]):
        catalog_map[key]["servers"].append({
            "name": item.get("server") or "Server",
            "type": item.get("type") or "iframe",
            "url": url
        })

catalog = sorted(
    catalog_map.values(),
    key=lambda x: (x["series"], -x["episode"])
)

with open("data/catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Merged {len(catalog)} episodes into data/catalog.json")
