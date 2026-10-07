import requests

TESTS = [
    ("https://apiv2.nobitex.ir/v3/orderbook/USDTIRT", None),
    ("https://api.nobitex.ir/v3/orderbook/USDTIRT", None),
    ("https://api.wallex.ir/v1/markets", "USDTTMN"),
]

for url, needle in TESTS:
    print("=" * 60)
    print(url)
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        print("status:", r.status_code, "| size:", len(r.text))
        text = r.text
        i = text.find(needle) if needle else 0
        i = max(i, 0)
        print(text[i: i + 400])
    except Exception as exc:
        print("ERROR:", exc)
