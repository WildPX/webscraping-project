import json
import time
import requests
import re
import os
from bs4 import BeautifulSoup
from tqdm import tqdm


# nltk.download('stopwords')
FANDOM_SITE = f"https://elderscrolls.fandom.com/ru"
PAGES_NAMES_PATH = f"projects/ruelderscrolls/pages_characters.txt"
PAGES_NAMES_LIST = []
PAGES_CATEGORY = "category-page__member-link"
INVALID_PREFIXES = ["Участник", "Категория", "Шаблон", "Участница", "Обсуждение",
                    "Обсуждение участника", "Обсуждение", "Блог", "Блог участника"]
INVALID_CATEGORIES_PREFIXES = ["Необходима_замена_перевода!", "Незавершенные_статьи", "Необходим_источник!"]
START_URLS = [f"{FANDOM_SITE}/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%9F%D0%B5%D1%80%D1%81%D0%BE%D0%BD%D0%B0%D0%B6%D0%B8"]
INFOBOX_FIELDS = ["Раса", "Фракция", "Локация", "Квест", "Услуги", "Состояние"]

JSON_DIRECTORY = f"projects/ruelderscrolls/characters"
JSON_FILE = {}
JSON_PATH = ""

MAX_RETRIES = 3


def filter_page_name(page_name):
    if any(page_name.startswith(prefix) for prefix in INVALID_PREFIXES):
        return ""
    return page_name.replace(' ', '_')


def get_all_pages_names(start_url):
    """Get all pages names from Category page"""
    def write_pages_names_to_file():
        with open(PAGES_NAMES_PATH, "w", encoding="utf-8") as file:
            for page_name in PAGES_NAMES_LIST:
                file.write(page_name + "\n")
        print("Wrote PAGES_NAMES.")

    while True:
        time.sleep(1)
        response = requests.get(start_url)

        for attempt in range(MAX_RETRIES):
            if response.status_code == 200:
                break
            else:
                print(f"Error {response.status_code}. Retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(10)
                response = requests.get(start_url)

        # Get page html
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        next_button = soup.find('span', string='Следующая')

        # Filter names if they include unwanted prefixes
        # Plus replace " " to "_"
        current_page_names = [a.text for a in soup.select('.category-page__member-link')]
        filtered_names = [filter_page_name(name) for name in current_page_names]
        PAGES_NAMES_LIST.extend([name for name in filtered_names if name])

        # Repeat until there are no pages left
        if next_button:
            start_url = next_button.find_parent('a')['href']
        else:
            break

        # Update meter
        tqdm.write(f"Scraping pages... {len(PAGES_NAMES_LIST)} pages found", end="\r")

    # Write PAGES_NAMES_LIST to file
    write_pages_names_to_file()


def read_pages_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            pages = file.readlines()
        return [page.strip() for page in pages]
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []


def replace_yo_with_e(value):
    if isinstance(value, str):
        return value.replace("ё", "е")
    elif isinstance(value, dict):
        return {key: replace_yo_with_e(inner_value) for key, inner_value in value.items()}
    elif isinstance(value, list):
        return [replace_yo_with_e(inner_value) for inner_value in value]
    else:
        return value


def filter_category(str):
    # If it's in INVALID_CATEGORIES then None
    if str in INVALID_CATEGORIES_PREFIXES:
        return None

    # If has _(Skyrim) then None
    match = re.search(r'_\([A-Za-z]+\)', str)
    if match:
        return None

    # Replace "_" with spaces
    return str.replace('_', ' ')


def scrape_page(page_name):
    url = f"{FANDOM_SITE}/api.php?action=parse&page={page_name}&format=json&formatversion=2"
    response = requests.get(url)

    for attempt in range(MAX_RETRIES):
        if response.status_code == 200:
            break
        else:
            print(f"Error {response.status_code}. Retrying ({attempt + 1}/{MAX_RETRIES})...")
            time.sleep(10)
            response = requests.get(url)

    json_data = response.json()['parse']
    html = json_data['text']
    soup = BeautifulSoup(html, 'html.parser')

    # Create json
    current_json = {}
    # Title parsing
    current_json['title'] = json_data['title']

    # Infobox parsing
    infobox = soup.find('table', class_='infobox-main')

    for item in INFOBOX_FIELDS:
        current_json[item] = None

    if infobox:
        for row in infobox.find_all('tr'):
            cells = row.find_all('td')

            if len(cells) == 2:
                field = cells[0].text.strip()
                value = cells[1].text.strip()

                if field in INFOBOX_FIELDS:
                    current_json[field] = value

    # Categories parsing
    current_json['categories'] = []
    for current_category_data in json_data['categories']:
        category = current_category_data['category']
        this_category = filter_category(category)
        if this_category:
            current_json['categories'].append(this_category)

    # Text parsing
    paragraphs = soup.find_all('p')
    result_string = ' '.join(paragraph.get_text() for paragraph in paragraphs)
    current_json['text'] = result_string[:512]

    save_json(current_json)


def save_json(current_json):
    # Используем название страницы как имя файла
    filename = os.path.join(JSON_DIRECTORY, f"{current_json['title']}.json")

    # Сохраняем JSON в файл
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(current_json, file, ensure_ascii=False, indent=2)


# def load_json():
#     global JSON_FILE
#     try:
#         with open(JSON_PATH, 'r', encoding='utf-8') as file:
#             JSON_FILE = json.load(file)
#     except (FileNotFoundError, json.JSONDecodeError):
#         # If file not found or not valid JSON, initialize with an empty JSON object
#         JSON_FILE = {}


def add_to_json(json_data):
    new_json = {
        json_data['title']: {
            'desc': json_data['desc'],
            'categories': json_data['categories'],
        }
    }

    for field in INFOBOX_FIELDS:
        new_json[json_data['title']][field] = json_data[field]

    JSON_FILE.update(new_json)


def scrape_all_pages():
    for page in tqdm(PAGES_NAMES_LIST, desc="Scraping pages", unit="page"):
        scrape_page(page)


def main():
    global PAGES_NAMES_LIST
    # First step
    PAGES_NAMES_LIST = read_pages_from_file(PAGES_NAMES_PATH)
    if not PAGES_NAMES_LIST:
        for url in START_URLS:
            get_all_pages_names(url)
    else:
        print("Found PAGES_NAMES.")
    print(PAGES_NAMES_LIST[1000])
    # Second step
    # scrape_all_pages()

# main()
PAGES_NAMES_LIST = read_pages_from_file(PAGES_NAMES_PATH)
def scrape_all_pages_from(index):
    for page in range(index, len(PAGES_NAMES_LIST)):
        scrape_page(PAGES_NAMES_LIST[page])

scrape_all_pages_from(7963)