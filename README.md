# 📉 PricePulse

Watches product prices on any website and sends you a Telegram message when the price drops or reaches your target.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Alerts-Telegram-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![Automation](https://img.shields.io/badge/Type-Automation-2cb67d?style=flat-square)

## Features

- 🛒 Works with any shop: you set a CSS selector for the price
- 🔔 Alerts on every price drop and when your target price is reached
- 💾 Remembers the last seen prices between runs
- ⏰ Runs in a loop or once (for cron / Windows Task Scheduler)

## Quick start

```bash
git clone https://github.com/nikitavoid/price-pulse
cd price-pulse
pip install -r requirements.txt
cp .env.example .env   # Telegram bot token + your chat id
python pulse.py --once
```

To find your `CHAT_ID`, message [@userinfobot](https://t.me/userinfobot) in Telegram.

## Adding products

Edit `config.json`:

```json
{
  "name": "My headphones",
  "url": "https://shop.example/headphones",
  "selector": ".product-price",
  "target": 150
}
```

To get the selector, right-click the price in your browser → **Inspect** → copy its class.

## License

MIT
