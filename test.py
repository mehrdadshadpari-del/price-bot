import re

import requests

URLS = [
    "https://www.tgju.org/gold-chart",
    "https://www.tgju.org/currency",
    "https://arzdigital.com/gold/melted-gold-mithqal/",
    "https://charteix.com",
]
KEYWORDS = ["18 عیار", "18عیار", "تتر", "مثقال", "آبشده", "فردایی", "حاضر"]

for url in URLS:
    print("=" * 60)
    print(url)
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        print("status:", r.status_code, "| size:", len(r.text))
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text)
        for kw in KEYWORDS:
            i = text.find(kw)
            if i >= 0:
                print(f"[{kw}] ->", text[max(0, i - 20): i + 120])
            else:
                print(f"[{kw}] -> NOT FOUND")
    except Exception as exc:
        print("ERROR:", exc)
