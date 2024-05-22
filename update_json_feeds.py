import requests
import sqlite3
import time
import json
from datetime import datetime

# Database connection
conn = sqlite3.connect('zdi_advisories_v2.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS advisories (
                zdi_public TEXT,
                zdi_can TEXT,
                title TEXT,
                public_advisory TEXT,
                products JSON,
                responses JSON,
                discoverers JSON,
                cvss_version TEXT,
                cvss_score REAL,
                cvss_vector TEXT,
                cves JSON,
                published_date TEXT
            )''')

years = range(2005, 2025)  # Will need to update yearly
retry_after = 30  # Got 429 sooo, retry after 30 seconds if rate limited.

for year in years:
    url = f'https://www.zerodayinitiative.com/api/advisories/published/?year={year}'
    while url:
        response = requests.get(url)
        if response.status_code == 429:
            print(f"Rate limited. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            continue
        if response.status_code != 200:
            print(f"Failed to fetch data for year {year}, URL: {url}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            break
        data = response.json()
        if 'results' not in data:
            print(f"No results found in the response for year {year}, URL: {url}")
            print(f"Response: {data}")
            break
        for result in data['results']:
            zdi_public = result.get('zdi_public')
            zdi_can = result.get('zdi_can')
            title = result.get('title')
            public_advisory = result.get('public_advisory')
            products = json.dumps(result.get('products', []))
            responses = json.dumps(result.get('responses', []))
            discoverers = json.dumps(result.get('discoverers', []))
            cvss_version = result.get('cvss_version')
            cvss_score = result.get('cvss_score')
            cvss_vector = result.get('cvss_vector')
            cves = json.dumps(result.get('cves', []))
            published_date = result.get('published_date')

            c.execute('''INSERT OR REPLACE INTO advisories 
                        (zdi_public, zdi_can, title, public_advisory, products, responses, discoverers, cvss_version, cvss_score, cvss_vector, cves, published_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                      (zdi_public, zdi_can, title, public_advisory, products, responses, discoverers, cvss_version, cvss_score, cvss_vector, cves, published_date))
        
        url = data.get('next')  # Move to the next page

# Commit and close
conn.commit()
conn.close()
