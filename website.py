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

    results = es.search(index=INDEX_NAME, body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^1.1",
                           "Раса^1.0",
                           "Фракция^1.0",
                           "Локация^1.0",
                           "Квест^1.0",
                           "Услуги^0.8",
                           "Состояние^0.25",
                           "categories.category^1.1",
                           "text^1.0"],
                "fuzziness": "AUTO",
            }
        },
        "size": 10
    })

    hits = results.get('hits', {}).get('hits', [])
    return jsonify([hit['_source'] for hit in hits])


if __name__ == '__main__':
    website.run(debug=True)
