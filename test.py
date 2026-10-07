import re

import requests

URLS = [
    "https://www.tgju.org/profile/geram18",
    "https://www.tgju.org/profile/mesghal",
    "https://www.tgju.org/profile/crypto-tether",
]

for url in URLS:
    print("=" * 60)
    print(url)
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        print("status:", r.status_code, "| size:", len(r.text))
        found = re.findall(r'data-col="([^"]+)"[^>]*>\s*([^<]{1,40})<', r.text)
        for name, value in found[:25]:
            print(name, "=>", value.strip())
        if not found:
            print("no data-col found")
    except Exception as exc:
        print("ERROR:", exc)
