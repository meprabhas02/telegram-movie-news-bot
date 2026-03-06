import requests
import feedparser
import schedule
import time
import os
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")

CHANNELS = [
    os.getenv("CHANNEL_ID_1"),
    os.getenv("CHANNEL_ID_2")
]

RSS_FEEDS = [
    "https://telugu.filmibeat.com/rss/filmibeat-telugu-fb.xml",
    "https://www.gulte.com/feed",
    "https://www.greatandhra.com/rss/latest"
]

posted = set()

hashtags = "#Tollywood #TeluguMovies #TeluguCinema #MovieUpdates"


def send_photo(title, image):

    caption = f"🎬 {title}\n\n{hashtags}"

    for channel in CHANNELS:

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(url, data={
            "chat_id": channel,
            "photo": image,
            "caption": caption
        })


def check_news():

    for feed_url in RSS_FEEDS:

        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:

            if entry.link not in posted:

                title = entry.title
                image = None

                if "media_content" in entry:
                    image = entry.media_content[0]["url"]

                if image:
                    send_photo(title, image)

                posted.add(entry.link)


schedule.every(10).minutes.do(check_news)


def run_bot():

    while True:
        schedule.run_pending()
        time.sleep(5)


app = Flask(__name__)

@app.route("/")
def home():
    return "Telugu Movie News Bot Running"


def run_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_bot).start()

run_web()
