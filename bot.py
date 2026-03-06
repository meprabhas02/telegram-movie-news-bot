import requests
import feedparser
import schedule
import time
import os
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

RSS_URL = "https://www.filmibeat.com/rss/filmibeat-movies-fb.xml"

posted = set()

def check_news():
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries[:5]:
        if entry.link not in posted:

            message = f"🎬 Movie Update\n\n{entry.title}\n\nRead more:\n{entry.link}"

            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

            requests.post(url, data={
                "chat_id": CHANNEL_ID,
                "text": message
            })

            posted.add(entry.link)

schedule.every(10).minutes.do(check_news)

def run_bot():
    while True:
        schedule.run_pending()
        time.sleep(5)

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Movie Bot Running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_bot).start()

run_web()
