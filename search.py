import json
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import urllib3


# TODO: Fix this
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DIRECTORY_PATH = "projects/ruelderscrolls/characters_full"
INDEX_NAME = 'characters_index_v2'

SETTINGS_MAPPING = {
    "properties": {
        "title": {
            "type": "text",
            "analyzer": "characters_analyzer"
        },
        "Раса": {
            "type": "keyword"
        },
        "Фракция": {
            "type": "text",
            "analyzer": "characters_analyzer"
        },
        "Локация": {
            "type": "text",
            "analyzer": "characters_analyzer"
        },
        "Квест": {
            "type": "text",
            "analyzer": "characters_analyzer"
        },
        "Услуги": {
            "type": "text",
            "analyzer": "characters_analyzer"
        },
        "Состояние": {
            "type": "keyword"
        },
        "categories": {
            "type": "text",
            "analyzer": "characters_analyzer"
        },
        "text": {
            "type": "text",
            "analyzer": "characters_analyzer"
        }
    }
}

SETTINGS_MAIN = \
{
    "analysis": {
        "analyzer": {
            "characters_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "russian_stop", "russian_synonyms", "russian_stemmer"]
            }
        },
        "filter": {
            "russian_stop": {"type": "stop", "stopwords": "_russian_"},
            "russian_stemmer": {"type": "stemmer", "language": "russian"},
            "russian_synonyms": {
                "type": "synonym",
                "synonyms_path": "synonyms.txt"
            }
        }
    }
}

es = Elasticsearch(hosts=["https://localhost:9200"], basic_auth=('elastic', '2PWsymmVIN5KZ+57*Jb*'), verify_certs=False)


def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        try:
            es.indices.create(index=INDEX_NAME,
                              body={"mappings": SETTINGS_MAPPING, "settings": SETTINGS_MAIN})

            actions = []
            for filename in os.listdir(DIRECTORY_PATH):
                if os.path.splitext(filename)[1] == ".json":
                    file_path = os.path.join(DIRECTORY_PATH, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)
                        actions.append({"_index": INDEX_NAME, "_source": json_data})

            if actions:
                response = bulk(es, actions)
                es.indices.refresh(index=INDEX_NAME)

            print(f"Index \"{INDEX_NAME}\" created.")
        except Exception as e:
            print(f"Error creating index: {str(e)}")
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
