import csv
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, ChannelInvalidError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
import re


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_parser.log"),
        logging.StreamHandler()
    ]
)

api_id = '...'
api_hash = '...'


channels = ['mash', 'F_S_C_P']
res = {'mash': 'mash',
       'F_S_C_P': 'FSCP'}

csv_file = 'telegram_posts.csv'
MAX_POSTS = 1000


def extract_links(entities, message_text):
    links = []
    for entity in entities:
        if isinstance(entity, (MessageEntityTextUrl, MessageEntityUrl)):
            link_text = message_text[entity.offset: entity.offset + entity.length]
            link_url = entity.url if hasattr(entity, 'url') else link_text
            links.append({"name": link_text, "link": link_url})
    return links


def write_to_csv(file_path, data):
    fieldnames = ["title", "date", "post", "url", "tags", "links", "resource"]
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f'Записано {len(data)} сообщений в файл {file_path}')


def get_first_sentence(text):
    match = re.search(r'([^.?!]*[.?!])', text)
    return match.group(0).strip() if match else text


def parse_telegram_channels(api_id, api_hash, channels, max_posts, csv_file):
    posts_data = []
    post_count = 0

    with TelegramClient('session_name', api_id, api_hash) as client:
        for channel_name in channels:
            logging.info(f'Обработка канала: {channel_name}')
            try:
                channel = client.get_entity(channel_name)
                client(GetFullChannelRequest(channel))

                async for message in client.iter_messages(channel, limit=max_posts):
                    if post_count >= max_posts:
                        break

                    title = get_first_sentence(message.message) if message.message else ''
                    date = message.date
                    post = message.message or ''
                    url = f"https://t.me/{channel.username}/{message.id}"
                    tags = re.findall(r"#\w+", post)
                    links = extract_links(message.entities or [], post)
                    resource = channel_name

                    posts_data.append({
                        "title": title,
                        "date": date,
                        "post": post,
                        "url": url,
                        "tags": tags,
                        "external_links": links,
                        "source": res[resource]
                    })

                    post_count += 1
                    if post_count >= max_posts:
                        break

                logging.info(f'Канал {channel_name} успешно обработан. Собрано сообщений: {len(posts_data)}')

            except ChannelPrivateError:
                logging.warning(f'Канал {channel_name} является приватным или доступ к нему ограничен.')
            except ChannelInvalidError:
                logging.warning(f'Канал {channel_name} не существует или неверный username.')
            except Exception as e:
                logging.error(f'Ошибка при обработке канала {channel_name}: {e}')

        write_to_csv(csv_file, posts_data)


if __name__ == "__main__":
    start_time = datetime.now()
    parse_telegram_channels(api_id, api_hash, channels, MAX_POSTS, csv_file)
    end_time = datetime.now()
    logging.info(f'Скрипт выполнен за: {end_time - start_time}')
