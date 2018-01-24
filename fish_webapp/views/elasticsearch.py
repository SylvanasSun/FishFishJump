from flask import Blueprint

from fish_core.search_engine import ElasticsearchClient

elasticsearch = Blueprint('elasticsearch', __name__)

es_client = None


def init_elasticsearch_client(hosts):
    global es_client
    es_client = ElasticsearchClient()
    es_client.from_normal(hosts=hosts)


@elasticsearch.route('/cluster/health', methods=['GET'])
def cluster_health_info():
    pass
