import requests
import feedparser
import schedule
import time

TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "-100XXXXXXXX"

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

while True:
    schedule.run_pending()
    time.sleep(5)
