import requests
import feedparser
import time
import os
import threading
import re
import hashlib
from flask import Flask
from PIL import Image, ImageDraw

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

posted_links = set()
posted_titles = set()


# ---------------- DUPLICATE CHECK ----------------

def is_duplicate(title):

    key = hashlib.md5(title.lower().strip().encode()).hexdigest()

    if key in posted_titles:
        return True

    posted_titles.add(key)

    return False


# ---------------- HASHTAGS ----------------

def generate_hashtags(title):

    words = re.findall(r"[A-Za-z]+", title)

    tags = []

    for w in words[:3]:
        tags.append("#" + w.capitalize())

    tags.append("#Tollywood")
    tags.append("#TeluguMovies")

    return " ".join(tags)


# ---------------- IMAGE EXTRACTOR ----------------

def extract_image(url):

    try:

        html = requests.get(url, timeout=10).text

        match = re.search(r'<img[^>]+src="([^">]+)"', html)

        if match:
            return match.group(1)

    except:
        return None


# ---------------- BLOG IMAGE GENERATOR ----------------

def create_blog_image(title):

    img = Image.new("RGB", (900, 450), color=(25,25,25))

    draw = ImageDraw.Draw(img)

    draw.text((50,200), title[:60], fill=(255,255,255))

    path = "blog_auto.jpg"

    img.save(path)

    return path


# ---------------- TELEGRAM SEND ----------------

def send_photo(caption, image):

    for channel in CHANNELS:

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(url, data={
            "chat_id": channel,
            "photo": image,
            "caption": caption
        })


# ---------------- BLOG POSTS ----------------

def check_blog():

    feed = feedparser.parse(BLOG_RSS)

    for entry in feed.entries:

        if entry.link in posted_links:
            continue

        title = entry.title
        link = entry.link

        hashtags = generate_hashtags(title)

        image = extract_image(link)

        caption = f"🎬 {title}\n\nRead full news:\n{link}\n\n{hashtags}"

        # Blog can post without image
        if image:
            send_photo(caption, image)
        else:
            auto_image = create_blog_image(title)
            send_photo(caption, auto_image)

        posted_links.add(entry.link)


# ---------------- NEWS POSTS ----------------

def check_news():

    for feed_url in NEWS_RSS:

        feed = feedparser.parse(feed_url)

        for entry in feed.entries:

            if entry.link in posted_links:
                continue

            if is_duplicate(entry.title):
                continue

            title = entry.title
            link = entry.link

            hashtags = generate_hashtags(title)

            image = extract_image(link)

            # News must have image
            if not image:
                continue

            caption = f"🎬 {title}\n\n{hashtags}"

            send_photo(caption, image)

            posted_links.add(entry.link)


# ---------------- BOT LOOP ----------------

def run_bot():

    while True:

        check_blog()
        check_news()

        time.sleep(300)


# ---------------- RENDER SERVER ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Telugu Movie Bot Running"


def run_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_bot).start()

run_web()
