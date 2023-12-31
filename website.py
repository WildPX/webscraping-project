from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch

website = Flask(__name__)

es = Elasticsearch(hosts=["https://localhost:9200"], basic_auth=('elastic', '2PWsymmVIN5KZ+57*Jb*'), verify_certs=False)
INDEX_NAME = 'characters_index_v2'

@website.route('/')
def index():
    return render_template('index.html')

@website.route('/search')
def search():
    query = request.args.get('query', '')

    # results = es.search(index=INDEX_NAME, body={
    #     "query": {
    #         "bool": {
    #             "should": [
    #                 {"match": {"title": {"query": query, "boost": 2}}},
    #                 {"match": {"categories.category": {"query": query}}},
    #                 {"match": {"text": {"query": query, "boost": 1.2}}},
    #                 {"match": {"Раса": {"query": query, "boost": 1.5}}},
    #                 {"match": {"Фракция": {"query": query, "boost": 0.8}}},
    #                 {"match": {"Локация": {"query": query, "boost": 1.2}}},
    #                 {"match": {"Квест": {"query": query, "boost": 0.9}}},
    #                 {"match": {"Состояние": {"query": query, "boost": 0.5}}}
    #             ]
    #         }
    #     }
    # })

    # results = es.search(index=INDEX_NAME, body={
    #     "query": {
    #         "multi_match": {
    #             "query": query,
    #             "fields": ["title^1.1",
    #                        "Раса.keyword^1.0",
    #                        "Фракция^1.25",
    #                        "Локация^1.0",
    #                        "Квест^1.0",
    #                        "Услуги^0.8",
    #                        "Состояние^0.5",
    #                        "categories^1.0",
    #                        "text^1.25"],
    #             "fuzziness": "1.0",
    #         }
    #     },
    #     "size": 10
    # })

    results = es.search(index=INDEX_NAME, body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^4.0",
                           "categories^4.0",
                           "text^3.0",
                           "Раса^2.5",
                           "Локация^2.0",
                           "Фракция^1.5",
                           "Квест^3.0",
                           "Услуги^0.8",
                           "Состояние^0.75"],
                "fuzziness": "0.0",
            }
        },
        "size": 10
    })

    hits = results.get('hits', {}).get('hits', [])
    return jsonify([hit['_source'] for hit in hits])


if __name__ == '__main__':
    website.run(debug=True)
