import json
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "@academymehrdad")
CHANNEL_TAG = "@academymehrdad"

TEHRAN = ZoneInfo("Asia/Tehran")
STATE_FILE = "state.json"

# ساعت‌هایی (به وقت تهران) که قیمت‌ها در کانال ارسال می‌شوند
SLOTS = [9, 12, 15, 18, 21]

MAZANNEH_FACTOR = 4.3318  # قیمت هر گرم ۱۸ عیار × این عدد = مظنه (مثقال)

HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_gold18_toman():
    r = requests.get("https://www.tgju.org/profile/geram18", timeout=30, headers=HEADERS)
    r.raise_for_status()
    m = re.search(r'data-col="info\.last_trade\.PDrCotVal"[^>]*>\s*([\d,]+)', r.text)
    if not m:
        raise ValueError("gold price not found on tgju")
    rial = int(m.group(1).replace(",", ""))
    return rial // 10  # tgju قیمت را به ریال می‌نویسد


def get_tether_toman():
    try:
        r = requests.get("https://apiv2.nobitex.ir/v3/orderbook/USDTIRT", timeout=30, headers=HEADERS)
        r.raise_for_status()
        return int(r.json()["lastTradePrice"]) // 10  # نوبیتکس ریال می‌دهد
    except Exception as exc:
        print(f"nobitex failed: {exc}", file=sys.stderr)
    r = requests.get("https://api.wallex.ir/v1/markets", timeout=30, headers=HEADERS)
    r.raise_for_status()
    m = re.search(r'"USDTTMN":\{.*?"lastPrice":"([\d.]+)"', r.text, re.S)
    if not m:
        raise ValueError("tether price not found")
    return int(float(m.group(1)))  # والکس تومان می‌دهد


def fmt(n):
    return f"{n:,}"


def build_message(now, tether, gram18, mazanneh):
    return (
        "💰 <b>قیمت لحظه‌ای بازار</b>\n\n"
        f"🟢 تتر: {fmt(tether)} تومان\n"
        f"🥇 طلای ۱۸ عیار (هر گرم): {fmt(gram18)} تومان\n"
        f"🥇 مظنه (مثقال): {fmt(mazanneh)} تومان\n\n"
        f"🕐 ساعت {now:%H:%M} به وقت تهران\n\n"
        f"{CHANNEL_TAG}"
    )


def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
        timeout=30,
    )
    r.raise_for_status()


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def main():
    now = datetime.now(TEHRAN)
    force = os.environ.get("FORCE_SEND") == "1"
    slot_key = f"{now:%Y-%m-%d}-{now.hour}"
    state = load_state()

    if not force:
        if now.hour not in SLOTS or state.get("last_slot") == slot_key:
            print("nothing to do now")
            return

    try:
        gram18 = get_gold18_toman()
        tether = get_tether_toman()
    except Exception as exc:
        print(f"price fetch failed, will retry next run: {exc}", file=sys.stderr)
        return

    mazanneh = round(gram18 * MAZANNEH_FACTOR / 1000) * 1000
    send(build_message(now, tether, gram18, mazanneh))

    if not force:
        state["last_slot"] = slot_key
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
