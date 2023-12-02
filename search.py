import json
import os
from elasticsearch import Elasticsearch
import urllib3


# TODO: Fix this
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIRECTORY_PATH = "projects/ruelderscrolls/characters"
INDEX_NAME = 'characters_index_v2'

SETTINGS_MAPPING = {
    "properties": {
        "title": {"type": "text", "analyzer": "russian"},
        "Раса": {"type": "keyword"},
        "Фракция": {"type": "text", "analyzer": "russian"},
        "Локация": {"type": "text", "analyzer": "russian"},
        "Квест": {"type": "text", "analyzer": "russian"},
        "Услуги": {"type": "text", "analyzer": "russian"},
        "Состояние": {"type": "text", "analyzer": "russian"},
        "categories": {
            "type": "nested",
            "properties": {
                "category": {"type": "text", "analyzer": "russian"},
            }
        },
        "text": {"type": "text", "analyzer": "russian"}
    }
}

SETTINGS_MAIN = {
    "settings": {
        "analysis": {
            "analyzer": {
                "russian": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_morphology", "russian_stop", "russian_stemmer", "russian_synonyms"]
                },
                "russian_typo": {
                    "tokenizer": "standard",
                    "filter": ["russian_typo"]
                },
            },
            "filter": {
                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                "russian_stemmer": {"type": "stemmer", "language": "russian"},
                "russian_synonyms": {
                    "type": "synonym",
                    "ignore_case": "true",
                    "synonyms_path": "projects/ruelderscrolls/synonyms.txt"
                },
                "russian_typo": {
                    "type": "phonetic",
                    "encoder": "russian",
                    "replace": True
                }
            }
        }
    }
}

es = Elasticsearch(hosts=["https://localhost:9200"], basic_auth=('elastic', '2PWsymmVIN5KZ+57*Jb*'), verify_certs=False)


def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        try:
            es.indices.create(index=INDEX_NAME,
                              body={"mappings": SETTINGS_MAPPING, "settings": SETTINGS_MAIN},
                              ignore=400)

            for filename in os.listdir(DIRECTORY_PATH):
                if os.path.splitext(filename)[1] == ".json":
                    file_path = os.path.join(DIRECTORY_PATH, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)
                        es.index(index=INDEX_NAME, body=json_data)

            print(f"Index \"{INDEX_NAME}\" created.")
        except Exception as e:
            print(f"Error creating index: {e}")
    else:
        print(f"Index \"{INDEX_NAME}\" already exists.")


def delete_index():
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"Index \"{INDEX_NAME}\" deleted successfully.")
    else:
        print(f"Index \"{INDEX_NAME}\" does not exist.")


def search(search_query):
    results = es.search(index=INDEX_NAME, body={
        "query": {
            "match": {
                "title": search_query
            }
        }
    })
    return results


def main():
    # Step 0
    delete_index()
    # Step 1
    create_index()
    # Step 2

main()