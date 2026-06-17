import os
import random
import re
import sqlite3
import json
from datetime import datetime, timezone, timedelta
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
    "App အလန်းလေး တွေ့ပြန်ပြီ <b>🌠</b>",
    "ဒါလေးက အသုံးဝင်မယ့် အရာပဲ 💎",
    "Android free app အသစ်တွေ့ပြီ <b>🍃</b>",
    "ဒီ App လေးက တကယ် အမိုက်စားပဲ 😎",
    "အသစ်တွေ့တာလေး ရှိတယ် 🍬",
    "ဒါလေးက အဆင်ပြေမလား စမ်းကြည့်ပါ 🎯",
    "AlternativeTo ကနေ အသစ်တွေ့ပြန်ပြီ 📡"
]

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
DB_PATH = ROOT / "watcher.db"
JSON_PATH = ROOT / "watcher.json"
RSS_PATH = DIST_DIR / "feed.xml"
INDEX_PATH = DIST_DIR / "index.html"


def ensure_dirs() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> dict:
    """Loads state from JSON, migrating from SQLite if JSON doesn't exist but SQLite does."""
    state = {
        "last_checked": None,
        "seen": {}
    }

    # 1. If JSON already exists, load from it
    if JSON_PATH.exists():
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                state["last_checked"] = loaded.get("last_checked")
                state["seen"] = loaded.get("seen", {})
                return state
        except Exception as e:
            print(f"Error loading JSON, falling back: {e}")

    # 2. If JSON does not exist but SQLite DB does, migrate the data
    if DB_PATH.exists():
        print("Migrating existing data from SQLite watcher.db to JSON...")
        try:
            conn = sqlite3.connect(DB_PATH)
            # Check if seen table exists
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seen'")
            if cur.fetchone():
                cur = conn.execute("SELECT item_id, title, link, first_seen FROM seen")
                for row in cur.fetchall():
                    item_id, title, link, first_seen = row
                    state["seen"][item_id] = {
                        "title": title,
                        "link": link,
                        "first_seen": first_seen or datetime.now(timezone.utc).isoformat()
                    }
                conn.close()
                state["last_checked"] = datetime.now(timezone.utc).isoformat()

                # Save the migrated data immediately
                save_data(state)
                print(f"Successfully migrated {len(state['seen'])} items from SQLite to JSON.")

                # Rename the database for safety
                try:
                    DB_PATH.rename(DB_PATH.with_suffix(".db.bak"))
                    print("Renamed watcher.db to watcher.db.bak to prevent future migrations.")
                except Exception as e:
                    print(f"Could not rename watcher.db: {e}")
            else:
                conn.close()
        except Exception as e:
            print(f"Error during migration from SQLite: {e}")

    return state


def save_data(state: dict) -> None:
    """Saves state to JSON file with nice formatting for readability and git diffs."""
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON state: {e}")


def prune_old_items(state: dict, days: int = 30) -> int:
    """Prunes items older than `days` from the state. Returns the count of pruned items."""
    now = datetime.now(timezone.utc)
    limit_date = (now - timedelta(days=days)).isoformat()

    initial_count = len(state["seen"])

    # Filter the seen items dictionary to keep only items newer than the limit_date
    state["seen"] = {
        item_id: info
        for item_id, info in state["seen"].items()
        if info.get("first_seen", "") >= limit_date
    }

    pruned_count = initial_count - len(state["seen"])
    if pruned_count > 0:
        print(f"Pruned {pruned_count} items older than {days} days from database.")
    return pruned_count


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


def build_rss(items: list[dict], state: dict) -> None:
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

        # Use stored first_seen date to keep the feed's dates accurate
        item_state = state["seen"].get(item["id"], {})
        first_seen_str = item_state.get("first_seen")
        if first_seen_str:
            try:
                # fromisoformat handles 'Z' or offset if standard, 
                # but let's parse robustly
                if first_seen_str.endswith("+00:00"):
                    first_seen_str = first_seen_str.replace("+00:00", "Z")
                pub_date = datetime.fromisoformat(first_seen_str.replace("Z", "+00:00"))
            except ValueError:
                pub_date = datetime.now(timezone.utc)
        else:
            pub_date = datetime.now(timezone.utc)

        fe.pubDate(pub_date)

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
      body {{{{ font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; line-height: 1.6; }}}}
      code, a {{{{ word-break: break-word; }}}}
      .card {{{{ padding: 16px; border: 1px solid #ddd; border-radius: 12px; }}}}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>{RSS_TITLE}</h1>
      <p>{RSS_DESCRIPTION}</p>
      <p>စုစုပေါင်း item: <strong>{total_count}</strong></p>
      <p>အသစ်တွေ့: <strong>{new_count}</strong></p>
      <p><a href="{{rss_url}}">RSS feed ကိုဖွင့်မယ်</a></p>
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
    state = load_data()

    # If last_checked is None, or state["seen"] is empty, it's a cold start
    is_cold_start = (state["last_checked"] is None or len(state["seen"]) == 0)

    try:
        html = fetch_html(TARGET_URL)
    except Exception as e:
        error_msg = f"❌ <b>AlternativeTo RSS Error</b>: Failed to fetch AlternativeTo page.\nError: {e}"
        print(error_msg)
        telegram_send(error_msg)
        return

    items = parse_items(html)

    # ⚠️ CSS Selector/Parsing Flaw Detection
    if len(items) == 0:
        warning_msg = (
            "⚠️ <b>AlternativeTo RSS Warning</b>: No items were parsed from AlternativeTo page!\n"
            "CSS selectors might have changed, or access is blocked."
        )
        print(warning_msg)
        telegram_send(warning_msg)
        return

    # Check for new items since the last run
    new_items = []
    for item in items:
        if item["id"] not in state["seen"]:
            # Record first seen time
            state["seen"][item["id"]] = {
                "title": item["title"],
                "link": item["link"],
                "first_seen": datetime.now(timezone.utc).isoformat()
            }
            new_items.append(item)

    # Prune items older than 30 days to keep file size small
    prune_old_items(state, days=30)

    # Build RSS feed with the correct publication dates and index page
    build_rss(items, state)
    build_index(len(new_items), len(items))

    # Send alerts if there are new items and it's not a cold start
    if new_items:
        if is_cold_start:
            print("Cold start detected. Saved items to JSON without sending Telegram alerts.")
        else:
            for item in new_items[:10]:
                random_text = random.choice(RANDOM_PHRASES)
                message = f"<b>{random_text}</b>\n\n<b>{item['title']}</b>\n\n{item['link']}"
                telegram_send(message)

    # Update last_checked timestamp and save the data
    state["last_checked"] = datetime.now(timezone.utc).isoformat()
    save_data(state)

    print(f"done: {len(items)} items, {len(new_items)} new")


if __name__ == "__main__":
    main()
