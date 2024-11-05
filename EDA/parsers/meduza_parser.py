import glob
import json
import locale
import re
import time
from datetime import datetime
from typing import cast

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from unicodedata2 import normalize

stream = 'https://meduza.io/api/w5/new_search?chrono=news&page={page}&per_page=30&locale=ru'
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0"
default_link_name = ["Конфиденциальность", "условия использования", "Подробнее про «Сигнал»"]
date_format = "%H:%M, %d %B %Y"
source = 'Источник: '
source_link_prefix = '<a href'

START_SEARCH_PAGE = 0
END_SEARCH_PAGE = 50
DIRECTORY_SAVE_NEWS = 'meduza_dump/'


def get_source(page_content):
    source_result = {}
    meta_list = page_content.findAll('div', attrs={'data-testid': 'meta-item'})
    for meta in meta_list:
        tag_element: Tag = cast(Tag, meta)
        if source in tag_element.contents:
            source_content = tag_element.contents
            if source_link_prefix in str(source_content[1]):
                match = re.search(r'href="([^"]+)".*?>(.*?)</a>', str(source_content[1]))
                url = match.group(1)
                name = match.group(2)
                source_result = {'url': url, 'name': name}
            else:
                source_result = {'name': str(source_content[2])}
    return source_result


def get_page_data(page, stream, user_agent, site_url="https://meduza.io/{0}"):
    headers = {'User-agent': user_agent}
    ans = requests.get(stream.format(page=page), headers=headers).json()
    urls = [site_url.format(key) for key in ans['documents'].keys()]
    print(urls)
    for url in urls:
        page_responce = requests.get(url, headers=headers, timeout=5)

        if page_responce.status_code == 200:
            page_content = BeautifulSoup(page_responce.content, "html.parser")
            textContent = []
            title = page_content.find_all("h1")[0].text
            date_string = page_content.find('time').contents[0]
            date = datetime.strptime(date_string, date_format).strftime('%Y-%m-%d %H:%M:%S')
            link = page_content.find_all("meta", property="og:url")[0]["content"]
            tags = page_content.find_all("meta", attrs={"name": "keywords"})[0]["content"]
            source_result = get_source(page_content)
            links = []
            for p in (page_content.find_all("p")):
                paragraphs = p.text
                textContent.append(normalize('NFKD', paragraphs))
                for a in p.find_all('a', href=True):
                    name = a.text.strip()
                    if name not in default_link_name:
                        links.append({
                            'name': name,
                            'link': a['href']
                        })

            body = "".join(textContent)

            new_title = normalize('NFKD', title)

            entry = {"title": new_title, "date": date, "text": body, "article_id": link, "tags": tags, "links": links,
                     "source": source_result}

            with open(DIRECTORY_SAVE_NEWS + 'page{pagenum:03d}_{timestamp}.json'.format(pagenum=page,
                                                                                        timestamp=int(time.time())),
                      'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)


def join_files_in_directory(directory_pattern):
    data = []
    for f in glob.glob(directory_pattern):
        with open(f, "rb") as infile:
            json_data = json.load(infile)
            data.append(json_data)
    df = pd.json_normalize(data)
    df = df.drop_duplicates(subset='article_id', keep='first')
    df = df.sort_values(by='date', ascending=False)
    df.insert(0, 'id', range(1, len(df) + 1))
    df.insert(1, 'source_type', 'Meduza')
    df.to_csv('meduza_news.csv', index=False, encoding='utf-8')
    return df


if __name__ == '__main__':
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    for page in range(START_SEARCH_PAGE, END_SEARCH_PAGE):
        get_page_data(page, stream, USER_AGENT)

    join_files_in_directory(f"./{DIRECTORY_SAVE_NEWS}*.json")
