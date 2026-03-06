import requests
import feedparser
import time
import os
from flask import Flask
import threading

TOKEN = os.getenv("BOT_TOKEN")

CHANNELS = [
    os.getenv("CHANNEL_ID_1"),
    os.getenv("CHANNEL_ID_2")
]

BLOG_RSS = "https://gkk-latest-updates.blogspot.com/feeds/posts/default?alt=rss"

NEWS_RSS = [
    "https://www.123telugu.com/feed",
    "https://telugu.filmibeat.com/rss/filmibeat-telugu-fb.xml",
    "https://www.gulte.com/feed",
    "https://www.greatandhra.com/rss/latest"
]

posted = set()


def generate_hashtags(title):

    words = title.split()

    tags = []

    for w in words[:3]:
        tag = w.replace(",", "").replace(".", "")
        tags.append("#" + tag)

    tags.append("#Tollywood")
    tags.append("#TeluguMovies")

    return " ".join(tags)


def send_photo(caption, image):

    for channel in CHANNELS:

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(url, data={
            "chat_id": channel,
            "photo": image,
            "caption": caption
        })


def check_blog():

    feed = feedparser.parse(BLOG_RSS)

    for entry in feed.entries[:5]:

        if entry.link not in posted:

            title = entry.title
            link = entry.link

            hashtags = generate_hashtags(title)

            image = None

            if "media_content" in entry:
                image = entry.media_content[0]["url"]

            caption = f"🎬 {title}\n\nRead full news:\n{link}\n\n{hashtags}"

            if image:
                send_photo(caption, image)

            posted.add(entry.link)


def check_news():

    for feed_url in NEWS_RSS:

        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:

            if entry.link not in posted:

                title = entry.title

                hashtags = generate_hashtags(title)

                image = None

                if "media_content" in entry:
                    image = entry.media_content[0]["url"]

                caption = f"🎬 {title}\n\n{hashtags}"

                if image:
                    send_photo(caption, image)

                posted.add(entry.link)


def run_bot():

    while True:
        check_blog()
        check_news()
        time.sleep(600)


app = Flask(__name__)

@app.route("/")
def home():
    return "Telugu Movie Bot Running"


def run_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_bot).start()

run_web()
