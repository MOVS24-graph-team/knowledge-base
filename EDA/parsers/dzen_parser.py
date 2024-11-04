# dzen news parser
#!/usr/bin/python3

import uuid
import json
import sqlite3
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# List of URLs to scrape
urls = [
    'https://dzen.ru/news',
    'https://dzen.ru/news/rubric/personal_feed',
    'https://dzen.ru/news/rubric/politics',
    'https://dzen.ru/news/rubric/society',
    'https://dzen.ru/news/rubric/business',
    'https://dzen.ru/news/rubric/svo',
    'https://dzen.ru/news/rubric/realty',
    'https://dzen.ru/news/rubric/energy',
    'https://dzen.ru/news/rubric/quotes',
    'https://dzen.ru/news/rubric/culture',
    'https://dzen.ru/news/rubric/movies',
    'https://dzen.ru/news/rubric/music',
    'https://dzen.ru/news/rubric/health',
    'https://dzen.ru/news/rubric/religion',
    'https://dzen.ru/news/rubric/travels',
    'https://dzen.ru/news/rubric/vehicle',
    'https://dzen.ru/news/rubric/communal',
    'https://sportsdzen.ru/news/rubric/sport',
    'https://sportsdzen.ru/news/rubric/cyber_sport',
    'https://sportsdzen.ru/news/rubric/football',
    'https://dzen.ru/news/rubric/computers',
    'https://dzen.ru/news/rubric/gadgets',
    'https://dzen.ru/news/rubric/internet',
    'https://dzen.ru/news/rubric/games',
    'https://dzen.ru/news/rubric/science',
    'https://dzen.ru/news/rubric/cosmos',
    'https://dzen.ru/news/rubric/showbusiness',
    'https://dzen.ru/news/rubric/auto'
]

# Set up Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument('--headless=new')

# Set up SQLite database connection and create table if not exists
conn = sqlite3.connect('news.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id TEXT PRIMARY KEY,
        title TEXT,
        link TEXT,
        content TEXT,
        yandex_link TEXT,
        post_date TEXT,
        rubric TEXT,
        post_links TEXT
    )
''')
conn.commit()

# Open browser and start scraping news links and details
with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options) as driver:
    # Step 1: Scrape links and titles from main pages
    news_links = []
    for url in urls:
        driver.get(url)
        sleep(2)

        # Scrape news elements based on CSS class names
        for news in driver.find_elements(By.CLASS_NAME, 'news-site--card-top-avatar__rootElement-1U'):
            elem = BeautifulSoup(news.get_attribute('innerHTML'), 'html.parser')
            title = elem.find_all('p')[-1].text.replace(u'\xa0', u' ')
            link = news.get_attribute('href')
            news_links.append(link)
            print(f"Scraped link: {title} - {link}")

        for news in driver.find_elements(By.CLASS_NAME, 'news-site--card-news__titleLink-2Q'):
            elem = BeautifulSoup(news.get_attribute('innerHTML'), 'html.parser')
            title = elem.find('div').text.replace(u'\xa0', u' ')
            link = news.get_attribute('href')
            news_links.append(link)
            print(f"Scraped link: {title} - {link}")

        for news in driver.find_elements(By.CLASS_NAME, 'news-card__link'):
            elem = BeautifulSoup(news.get_attribute('innerHTML'), 'html.parser')
            title = elem.find_all('span')[1].text.replace(u'\xa0', u' ')
            link = news.get_attribute('href')
            news_links.append(link)
            print(f"Scraped link: {title} - {link}")

    # Step 2: Scrape detailed information for each news link
    for yandex_link in news_links:
        driver.get(yandex_link)
        sleep(1.3)

        try:
            yandex_link = driver.current_url
            link = driver.find_element(By.CSS_SELECTOR, '.news-story-head-redesign__title a').get_attribute('href')
            title = driver.find_element(By.CSS_SELECTOR, '.news-story-head-redesign__title a').text
            content = ' '.join(span.text for span in driver.find_element(By.CLASS_NAME, 'news-story-redesign__digest').find_elements(By.TAG_NAME, 'span'))

            # Get all post links from the content
            post_links = [a.get_attribute('href') for a in driver.find_element(By.CLASS_NAME, 'news-story-redesign__digest').find_elements(By.TAG_NAME, 'a')]
            post_links_json = json.dumps(post_links)
            post_date = driver.find_element(By.CLASS_NAME, 'news-story-redesign__time').text

            # Extract rubric name from the URL
            rubric_match = re.search(r'rubric=([^&]+)', yandex_link)
            rubric = rubric_match.group(1) if rubric_match else None

            # Insert the news item into the SQLite database
            cursor.execute('''
                INSERT OR IGNORE INTO news (id, title, link, content, yandex_link, post_date, rubric, post_links)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                title,
                link,
                content,
                yandex_link,
                post_date,
                rubric,
                post_links_json
            ))
            conn.commit()
            print(f"Saved news: {title}")
        except Exception as e:
            print(f"Error fetching content for {yandex_link}: {e}")
            continue

# Close database connection
conn.close()
print("Completed scraping and saving news content.")
