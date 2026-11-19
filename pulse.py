"""PricePulse — watches product prices and pings you in Telegram when they drop.

Usage:
    python pulse.py            # check every N minutes (see config.json)
    python pulse.py --once     # single check, handy for cron / Task Scheduler
"""

import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

CONFIG = Path("config.json")
STATE = Path("prices.json")  # last seen prices
HEADERS = {"User-Agent": "Mozilla/5.0 (PricePulse/1.0)"}


def parse_price(text: str) -> float | None:
    """'1 299,90 BYN' -> 1299.9"""
    cleaned = re.sub(r"[^\d,.]", "", text.replace("\xa0", "").replace(" ", ""))
    if "," in cleaned and "." not in cleaned:
        cleaned = cleaned.replace(",", ".")
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def get_price(http: httpx.Client, url: str, selector: str) -> float | None:
    resp = http.get(url)
    resp.raise_for_status()
    node = BeautifulSoup(resp.text, "html.parser").select_one(selector)
    return parse_price(node.get_text()) if node else None


def notify(http: httpx.Client, text: str) -> None:
    token, chat_id = os.getenv("BOT_TOKEN"), os.getenv("CHAT_ID")
    if not (token and chat_id):
        print("[notify skipped: BOT_TOKEN / CHAT_ID not set]", text)
        return
    http.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
    )


def check(config: dict) -> None:
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20) as http:
        for item in config["products"]:
            name, url = item["name"], item["url"]
            try:
                price = get_price(http, url, item["selector"])
            except httpx.HTTPError as e:
                print(f"⚠️  {name}: {e}")
                continue
            if price is None:
                print(f"⚠️  {name}: price not found, check the selector")
                continue

            old = state.get(url)
            stamp = datetime.now().strftime("%H:%M")
            print(f"[{stamp}] {name}: {price} (was {old})")

            if old is not None and price < old:
                notify(http, f"📉 {name} got cheaper: {old} → {price}\n{url}")
            if price <= item.get("target", 0):
                notify(http, f"🎯 {name} hit your target price {item['target']}: now {price}\n{url}")
            state[url] = price
    STATE.write_text(json.dumps(state, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Track product prices")
    parser.add_argument("--once", action="store_true", help="run one check and exit")
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))

    while True:
        check(config)
        if args.once:
            break
        time.sleep(config.get("interval_minutes", 60) * 60)


if __name__ == "__main__":
    main()
