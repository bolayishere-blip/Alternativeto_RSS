import os
import random
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from curl_cffi import requests
from dotenv import load_dotenv
from feedgen.feed import FeedGenerator
from selectolax.lexbor import LexborHTMLParser

load_dotenv()

TARGET_URL = os.getenv(
    "TARGET_URL",
    "https://alternativeto.net/browse/all/?license=free&platform=android&sort=addeddate",
)
BASE_URL = os.getenv("BASE_URL", "https://alternativeto.net")
RSS_TITLE = os.getenv("RSS_TITLE", "AlternativeTo Android Free Apps")
RSS_LINK = os.getenv("RSS_LINK", TARGET_URL)
RSS_DESCRIPTION = os.getenv(
    "RSS_DESCRIPTION", "Newly added free Android apps from AlternativeTo"
)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RANDOM_PHRASES = [
    "အသစ်တွေ့တယ် 👀",
    "App အသစ်လေး တွေ့ပြီ ✨",
    "ဒါလေး ကြည့်ကြည့် 👀",
    "အသစ်တက်လာတာ ရှိတယ်နော် 🚀",
    "ဒီ App လေး စိတ်ဝင်စားဖို့ ကောင်းမယ် ထင်တယ် 🌟",
    "Bug တွေ ရှင်းပြီးသား App သစ်လေး တက်လာတယ် 🛠️",
    "ရှာနေတဲ့ App ဖြစ်မလား ကြည့်လိုက်ဦး 🔍",
    "AlternativeTo မှာ အသစ်တက်လာပြီ 📢",
    "ဒီနေ့အတွက် App အသစ်လေး 🎁",
    "ဒါလေး သုံးကြည့်ရင် ကောင်းမလား 💭",
    "အသစ်တွေ့တာလေး မျှဝေပေးမယ် 🤝",
    "App အလန်းလေး တစ်ခု တွေ့ပြန်ပြီ 🔥",
    "ဒါလေးက အသုံးဝင်မယ် ထင်တယ် 🛠️",
    "Android အတွက် အသစ်လေး တွေ့တယ် 🤖",
    "ဒီ App လေးကို စမ်းကြည့်ပါဦး 🧪",
    "အသစ်ထွက်လာတာ ရှိတယ် 👀",
    "စိတ်ဝင်စားစရာ App လေး တွေ့လို့ 🌈",
    "ဒါလေးက Free ဖြစ်ပြီး အသစ်တက်လာတာ 💸",
    "တွေ့တာနဲ့ ချက်ချင်း ပို့ပေးလိုက်တယ် ⚡",
    "App အသစ်လေး တစ်ခု တွေ့ပြန်ပြီ 💎",
    "ဒါလေးက အဆင်ပြေမလား ကြည့်ပါဦး ✅",
    "Android အသစ်လေး တွေ့ပြန်ပြီ 📱",
    "ဒီ App လေးက တကယ် အသုံးဝင်မယ် 🌟",
    "အသစ်တွေ့တာလေး တစ်ခုရှိတယ် 🧐",
    "ဒါလေး သုံးကြည့်ဖို့ အကြံပေးချင်တယ် 👍",
    "AlternativeTo ကနေ အသစ်တွေ့တာ 📡",
    "App အသစ်လေး တွေ့လို့ ပို့ပေးတာ 💌",
    "ဒါလေးက အလန်းပဲ ဖြစ်မယ် 💥",
    "အသစ်တက်လာတဲ့ App လေး တစ်ခု 🌙",
    "ဒီ App လေးကို သတိထားကြည့်ပါ ⚠️",
    "တွေ့တာနဲ့ ပို့ပေးလိုက်တာ 🏃‍♂️",
    "Android free app အသစ်လေး တွေ့ပြီ 🍀",
    "ဒါလေးက အသုံးဝင်မယ့် tool လေးပဲ ⚙️",
    "App အသစ်လေး တွေ့လို့ မျှဝေတာ ☀️",
    "ဒီ App လေး စမ်းသုံးကြည့်ပါဦး 🕹️",
    "အသစ်တွေ့တာလေး တစ်ခုရှိတယ်နော် 🎈",
    "ဒါလေးက တကယ် အဆင်ပြေမယ် 💯",
    "AlternativeTo မှာ အသစ်တက်လာပြန်ပြီ 📣",
    "App အသစ်လေး တစ်ခု တွေ့ပြန်ပြီ 🎇",
    "ဒါလေးက စိတ်ဝင်စားဖို့ ကောင်းတယ် 🌀",
    "Android အတွက် အသစ်လေး တွေ့တယ် 🔋",
    "ဒီ App လေးက အသုံးတည့်မယ် ထင်တယ် 📌",
    "အသစ်တွေ့တာလေး ပို့ပေးလိုက်တယ် 📮",
    "ဒါလေးက အသစ်ပဲ၊ ကြည့်လိုက်ဦး 👁️",
    "App အလန်းလေး တွေ့ပြန်ပြီ 🌠",
    "ဒါလေးက အသုံးဝင်မယ့် အရာပဲ 💎",
    "Android free app အသစ်တွေ့ပြီ 🍃",
    "ဒီ App လေးက တကယ် အမိုက်စားပဲ 😎",
    "အသစ်တွေ့တာလေး ရှိတယ် 🍬",
    "ဒါလေးက အဆင်ပြေမလား စမ်းကြည့်ပါ 🎯",
    "AlternativeTo ကနေ အသစ်တွေ့ပြန်ပြီ 📡"
]

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
DB_PATH = ROOT / "watcher.db"
RSS_PATH = DIST_DIR / "feed.xml"
INDEX_PATH = DIST_DIR / "index.html"


def ensure_dirs() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS seen (
            item_id TEXT PRIMARY KEY,
            title TEXT,
            link TEXT,
            first_seen TEXT
        )
        """
    )
    return conn


def fetch_html(url: str) -> str:
    session = requests.Session()
    resp = session.get(url, impersonate="chrome", timeout=30)
    resp.raise_for_status()
    return resp.text


def make_id(link: str, title: str) -> str:
    return re.sub(r"\s+", " ", f"{link}|{title}").strip()


def parse_items(html: str):
    parser = LexborHTMLParser(html)
    items = []

    selectors = ["article", ".item", ".app", ".browse__item", ".gridItem"]
    for selector in selectors:
        for card in parser.css(selector):
            a = card.css_first("a[href]")
            title_node = card.css_first("h2, h3, .title, .browse__item-title")
            if not a or not title_node:
                continue

            title = title_node.text(strip=True)
            href = a.attributes.get("href", "")
            link = urljoin(BASE_URL, href)
            if not title or not link:
                continue

            desc_node = card.css_first("p, .description, .browse__item-description")
            desc = desc_node.text(strip=True) if desc_node else ""

               # အညွှန်းစာတိုတွေကို သန့်ရှင်းအောင်လုပ်မယ်
            items.append(
                {
                    "id": make_id(link, title),
                    "title": title,
                    "link": link,
                    "desc": desc,
                }
            )

    uniq = {}
    for item in items:
        uniq[item["id"]] = item
    return list(uniq.values())


def load_seen(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute("SELECT item_id FROM seen")
    return {row[0] for row in cur.fetchall()}


def save_seen(conn: sqlite3.Connection, item: dict) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO seen (item_id, title, link, first_seen) VALUES (?, ?, ?, ?)",
        (
            item["id"],
            item["title"],
            item["link"],
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()


def build_rss(items: list[dict]) -> None:
    fg = FeedGenerator()
    fg.title(RSS_TITLE)
    fg.link(href=RSS_LINK, rel="self")
    fg.link(href=BASE_URL, rel="alternate")
    fg.description(RSS_DESCRIPTION)
    fg.language("en")
    fg.id(RSS_LINK)
    fg.lastBuildDate(datetime.now(timezone.utc))

    for item in items[:100]:
        fe = fg.add_entry()
        fe.id(item["id"])
        fe.title(item["title"])
        fe.link(href=item["link"])
        if item["desc"]:
            fe.description(item["desc"])
        fe.pubDate(datetime.now(timezone.utc))

    fg.rss_file(str(RSS_PATH), pretty=True)


def build_index(new_count: int, total_count: int) -> None:
    rss_url = "./feed.xml"
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{RSS_TITLE}</title>
    <style>
      body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; line-height: 1.6; }}
      code, a {{ word-break: break-word; }}
      .card {{ padding: 16px; border: 1px solid #ddd; border-radius: 12px; }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>{RSS_TITLE}</h1>
      <p>{RSS_DESCRIPTION}</p>
      <p>စုစုပေါင်း item: <strong>{total_count}</strong></p>
      <p>အသစ်တွေ့: <strong>{new_count}</strong></p>
      <p><a href="{rss_url}">RSS feed ကိုဖွင့်မယ်</a></p>
    </div>
  </body>
</html>
"""
    INDEX_PATH.write_text(html, encoding="utf-8")


def telegram_send(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    session = requests.Session()
    resp = session.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def main() -> None:
    if not TARGET_URL:
        raise RuntimeError("TARGET_URL is missing")

    ensure_dirs()
    conn = db()
    seen = load_seen(conn)

    is_cold_start = (len(seen) == 0)

    html = fetch_html(TARGET_URL)
    items = parse_items(html)
    new_items = [item for item in items if item["id"] not in seen]

    for item in new_items:
        save_seen(conn, item)

    build_rss(items)
    build_index(len(new_items), len(items))

    if new_items:
        if is_cold_start:
            print("Cold start detected. Saved items to database without sending Telegram alerts.")
        else:
            for item in new_items[:10]:
                random_text = random.choice(RANDOM_PHRASES)
                message = f"<b>{random_text}</b>\n\n<b>{item['title']}</b>\n\n{item['link']}"
                telegram_send(message)

    conn.close()
    print(f"done: {len(items)} items, {len(new_items)} new")


if __name__ == "__main__":
    main()