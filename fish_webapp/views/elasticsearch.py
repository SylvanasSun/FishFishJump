from fish_webapp.cache import is_cacheable, get_cached, set_cached, CacheKeys
from flask import Blueprint, current_app, jsonify

from fish_core.search_engine import ElasticsearchClient

elasticsearch = Blueprint('elasticsearch', __name__)

es_client = None

is_auto_transfer = False


def init_elasticsearch_client(hosts):
    global es_client
    es_client = ElasticsearchClient()
    es_client.from_normal(hosts=hosts)


@elasticsearch.route('/cluster/health/', methods=['GET'])
def cluster_health_info():
    if is_cacheable(current_app, CacheKeys.ELASTICSEARCH_CLUSTER_HEALTH):
        return jsonify(get_cached(current_app, CacheKeys.ELASTICSEARCH_CLUSTER_HEALTH))
    else:
        result = es_client.cluster_health()
        set_cached(current_app, CacheKeys.ELASTICSEARCH_CLUSTER_HEALTH, result)
        return jsonify(result)


@elasticsearch.route('/auto/transfer/status', methods=['GET'])
def auto_transfer_status():
    global is_auto_transfer
    return jsonify({'is_auto_transfer': is_auto_transfer})


@elasticsearch.route('/auto/transfer/status/change', methods=['GET'])
def change_auto_transfer_status():
    global is_auto_transfer
    result = {'prev_status': is_auto_transfer, 'result': 'fail'}
    is_auto_transfer = not is_auto_transfer
    result['result'] = 'success'
    return jsonify(result)
