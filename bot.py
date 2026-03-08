import requests
import feedparser
import time
import os
import threading
import re
import json
from flask import Flask
from PIL import Image, ImageDraw
import google.generativeai as genai

# -------- API KEYS --------

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-pro")

CHANNELS = [
    os.getenv("CHANNEL_ID_1"),
    os.getenv("CHANNEL_ID_2")
]

BLOG_RSS = "https://gkk-latest-updates.blogspot.com/feeds/posts/default?alt=rss"

posted_links = set()


# -------- AI CAPTION + HASHTAGS --------

def ai_caption(title):

    try:

        prompt = f"""
Write a short Telegram caption for this Telugu movie news.
Title: {title}

Rules:
- 1 short sentence
- Generate 5 English hashtags
- Return only caption and hashtags
"""

        response = model.generate_content(prompt)

        return response.text.strip()

    except:
        return f"{title}\n\n#Tollywood #TeluguMovies"


# -------- IMAGE EXTRACTOR --------

def extract_image(url):

    try:

        html = requests.get(url, timeout=10).text

        match = re.search(r'<meta property="og:image" content="([^"]+)"', html)

        if match:
            return match.group(1)

    except:
        return None


# -------- AUTO IMAGE GENERATOR --------

def create_blog_image(title):

    img = Image.new("RGB", (900, 450), color=(20,20,20))

    draw = ImageDraw.Draw(img)

    draw.text((40,200), title[:60], fill=(255,255,255))

    path = "auto_blog.jpg"

    img.save(path)

    return path


# -------- TELEGRAM POST --------

def send_photo(caption, image, link):

    keyboard = {
        "inline_keyboard": [
            [{"text": "👉 Read Full Article", "url": link}]
        ]
    }

    for channel in CHANNELS:

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        requests.post(url, data={
            "chat_id": channel,
            "photo": image,
            "caption": caption,
            "reply_markup": json.dumps(keyboard)
        })


# -------- BLOG CHECK --------

def check_blog():

    feed = feedparser.parse(BLOG_RSS)

    for entry in feed.entries:

        if entry.link in posted_links:
            continue

        title = entry.title
        link = entry.link

        caption = "🎬 " + ai_caption(title)

        image = extract_image(link)

        if image:
            send_photo(caption, image, link)
        else:
            auto_image = create_blog_image(title)
            send_photo(caption, auto_image, link)

        posted_links.add(link)


# -------- BOT LOOP --------

def run_bot():

    while True:

        check_blog()

        time.sleep(300)


# -------- RENDER SERVER --------

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Blogger Telegram Bot Running"


def run_web():

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_bot).start()

run_web()
