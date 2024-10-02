from elasticsearch import Elasticsearch

es = Elasticsearch(
    ['http://localhost:9200'],
    http_auth=('user', 'password')
)