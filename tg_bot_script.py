import json
import time
import schedule
import requests
import os
from dotenv import load_dotenv
from bokuao_blog import get_latest_blog_url, parse_blog_detail

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Replace with your actual chat ID
CONFIG_FILE = 'blog_config.json'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def send_telegram_message(text):
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={
        "CHANNEL_ID": CHANNEL_ID,
        "text": text
    })

def send_media_group(images, title, url, writer, date):
    hashtags = f"#{writer.replace(' ', '')} #僕青ブログ"
    caption = f"🆕 {date}\n\n📌 <b>{title}</b>\n🔗 <a href=\"{url}\">blog link</a>\n\n{hashtags}"

    media = []
    for idx, img_url in enumerate(images):
        item = {
            "type": "photo",
            "media": img_url
        }
        if idx == 0:
            item["caption"] = caption
            item["parse_mode"] = "HTML"
        media.append(item)

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
        json={
            "CHANNEL_ID": CHANNEL_ID,
            "media": media
        }
    )


def send_telegram_photo(photo_url):
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", params={
        "CHANNEL_ID": CHANNEL_ID,
        "photo": photo_url
    })

def check_for_new_blog(entry):
    writer = entry["writer"]
    base_url = entry["base_url"]
    last_id = entry["last_blog_id"]

    latest_url = get_latest_blog_url(base_url)
    if not latest_url:
        print(f"❌ Failed to fetch blog list for {writer}.")
        return

    blog_id = latest_url.split("/")[-1]
    if blog_id == last_id:
        print(f"✅ No new blog for {writer}.")
        return

    blog_data = parse_blog_detail(latest_url)
    if blog_data["writer"] != writer:
        print(f"⚠️ Mismatched writer. Skipping: {blog_data['writer']}")
        return

    # send_telegram_message(f"🆕 {writer} の新ブログが投稿されました！\n\n📌 {blog_data['title']}\n🔗 {blog_data['url']}")
    print(f"🆕 {writer} の新ブログが投稿されました！\n\n📌 {blog_data['title']}\n🔗 {blog_data['url']}")
    send_media_group(blog_data["images"], blog_data["title"], blog_data["url"], blog_data["writer"], blog_data["date"])

    # Update ID in config
    entry["last_blog_id"] = blog_id
    print(f"✅ Sent blog by {writer}: {blog_data['title']}")

def job():
    config = load_config()
    for entry in config:
        check_for_new_blog(entry)
    save_config(config)

# Run every 10 minutes
schedule.every(10).minutes.do(job)

print("🔍 僕青ブログを監視中...")
job()

while True:
    schedule.run_pending()
    time.sleep(1)
