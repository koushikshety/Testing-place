import base64
import json
from bs4 import BeautifulSoup
import requests

TARGET_URL = "https://donghuastream.org/"
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

def inspect_site():
    report = {"target": TARGET_URL, "status_code": None, "cloudflare_blocked": False, "episodes_found": []}
    try:
        res = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        report["status_code"] = res.status_code

        if res.status_code in (403, 503) or "Just a moment..." in res.text:
            report["cloudflare_blocked"] = True
            print(f"[!] Blocked by WAF/Cloudflare (HTTP {res.status_code}).")
            with open("dummy_output.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            return

        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.select("article.bs a")[:5]
        print(f"[+] HTTP {res.status_code} OK — Found {len(cards)} cards.")

        for card in cards:
            ep_url = card.get("href")
            title = card.get("title") or card.text.strip()
            if not ep_url:
                continue

            ep_data = {"title": title, "url": ep_url, "servers": []}
            if len(report["episodes_found"]) == 0:
                ep_res = requests.get(ep_url, headers=HEADERS, timeout=15)
                ep_soup = BeautifulSoup(ep_res.text, "html.parser")

                default_iframe = ep_soup.select_one(".player-embed iframe, #pembed iframe")
                if default_iframe and default_iframe.get("src"):
                    ep_data["servers"].append({"name": "Default Player", "embed_url": default_iframe.get("src")})

                for opt in ep_soup.select("select.mirror option"):
                    val = opt.get("value", "").strip()
                    if val:
                        decoded_src = decode_base64_iframe(val)
                        if decoded_src:
                            ep_data["servers"].append({"name": opt.text.strip(), "embed_url": decoded_src})

            report["episodes_found"].append(ep_data)
    except Exception as e:
        report["error"] = str(e)
        print(f"[!] Request failed: {e}")

    with open("dummy_output.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("[+] Saved diagnostic results to dummy_output.json")

if __name__ == "__main__":
    inspect_site()
