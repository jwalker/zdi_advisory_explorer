import sqlite3
import feedparser
from datetime import datetime

# Initialize the database
def init_db():
    conn = sqlite3.connect('zdi_advisories.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS advisories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    link TEXT,
                    published DATE,
                    summary TEXT,
                    year INTEGER
                )''')
    conn.commit()
    conn.close()

# Function to fetch and parse RSS feeds
def fetch_rss_feed(year):
    url = f"https://www.zerodayinitiative.com/rss/published/{year}/"
    feed = feedparser.parse(url)
    return feed

# Function to parse entries from feed
def parse_feed(feed, year):
    entries = feed['entries']
    data = []
    for entry in entries:
        data.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary,
            'year': year
        })
    return data

# Update database with new RSS feed data
def update_db():
    conn = sqlite3.connect('zdi_advisories.db')
    c = conn.cursor()
    years = list(range(2005, 2025))
    for year in years:
        feed = fetch_rss_feed(year)
        data = parse_feed(feed, year)
        for item in data:
            c.execute('''INSERT INTO advisories (title, link, published, summary, year)
                         VALUES (?, ?, ?, ?, ?)''',
                      (item['title'], item['link'], item['published'], item['summary'], item['year']))
    conn.commit()
    conn.close()

# Initialize and update the database
init_db()
update_db()
