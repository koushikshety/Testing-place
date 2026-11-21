import base64
import json
from bs4 import BeautifulSoup
import requests

SEARCH_URL = "https://donghuastream.org/?s=renegade+immortal"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 14; iQOO Neo 10) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def decode_base64_iframe(encoded_str):
    try:
        decoded_html = base64.b64decode(encoded_str).decode("utf-8", errors="ignore")
        soup = BeautifulSoup(decoded_html, "html.parser")
        iframe = soup.find("iframe")
        return iframe.get("src") if iframe else None
    except Exception:
        return None

def fetch_renegade_immortal_rumble():
    report = {"target": SEARCH_URL, "status_code": None, "cloudflare_blocked": False, "episodes_found": []}

    res = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
    report["status_code"] = res.status_code
    soup = BeautifulSoup(res.text, "html.parser")

    series_link = None
    for a in soup.select("article.bs a"):
        href = a.get("href", "").lower()
        if "renegade-immortal" in href and "movie" not in href and "special" not in href:
            series_link = a.get("href")
            break

    if not series_link:
        print("[!] Could not find main Renegade Immortal series page.")
        return

    print(f"[+] Series page: {series_link}")
    s_res = requests.get(series_link, headers=HEADERS, timeout=15)
    s_soup = BeautifulSoup(s_res.text, "html.parser")
    latest_ep = s_soup.select_one(".eplister ul li a")

    if not latest_ep:
        print("[!] Could not find episode list.")
        return

    ep_url = latest_ep.get("href")
    ep_title = " ".join(latest_ep.text.split())
    print(f"[+] Latest episode: {ep_title}")

    ep_res = requests.get(ep_url, headers=HEADERS, timeout=15)
    ep_soup = BeautifulSoup(ep_res.text, "html.parser")

    servers = []
    for opt in ep_soup.select("select.mirror option"):
        val = opt.get("value", "").strip()
        if val:
            decoded_src = decode_base64_iframe(val)
            if decoded_src:
                servers.append({"name": opt.text.strip(), "embed_url": decoded_src})

    servers.sort(key=lambda s: 0 if "rumble" in s["name"].lower() or "rumble.com" in s["embed_url"].lower() else 1)

    report["episodes_found"].append({
        "title": ep_title,
        "url": ep_url,
        "servers": servers
    })

    with open("dummy_output.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved {len(servers)} servers to dummy_output.json")

if __name__ == "__main__":
    fetch_renegade_immortal_rumble()
