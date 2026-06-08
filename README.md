# AlternativeTo RSS Watcher

This repository watches the AlternativeTo Android free apps listing, generates an RSS feed, and publishes it with GitHub Pages.

## What it does

- Fetches the listing page with curl_cffi
- Parses app cards with selectolax
- Stores seen item IDs in SQLite
- Generates `dist/feed.xml`
- Generates `dist/index.html`
- Sends Telegram alerts for new items when bot secrets are set

## Setup

1. Add GitHub repository secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
2. Enable GitHub Pages in repository settings.
3. Set Pages source to **GitHub Actions**.
4. Push to `main` or run the workflow manually.

## Output

After a workflow run, the RSS feed will be published from the `dist/` folder.
