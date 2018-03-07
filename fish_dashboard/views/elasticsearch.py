#!/usr/bin/env python
# -*- coding: utf-8 -*-
import queue
import threading
import time

from flask import Blueprint, current_app, jsonify, request, Response

from fish_core.search_engine import ElasticsearchClient, get_documents_count_from_mongo
from fish_dashboard.cache import CacheKeys
from fish_dashboard.fault import fault_tolerant_by_backup

elasticsearch = Blueprint('elasticsearch', __name__)

es_client = None

is_auto_transfer = False

lock = threading.Lock()

auto_transfer_thread_id = None

transfer_data_info_queue = queue.Queue()


def init_elasticsearch_client(hosts):
    global es_client
    try:
        es_client = ElasticsearchClient()
        es_client.from_normal(hosts=hosts)
    except Exception:
        current_app.logger.warning('Connected Elasticsearch occurred error.')


def transfer_progress_event():
    try:
        transfer_data_info = transfer_data_info_queue.get(timeout=2)
    except queue.Empty as e:
        current_app.logger.warning('Illegal invoke, transfer data info is not in existence')
        current_app.logger.exception(e)
        return 'data: error\n\n'

    if transfer_data_info['filter_field'] == '':
        query_params = {}
    else:
        query_params = {transfer_data_info['filter_field']: False}
    try:
        transfer_volume = get_documents_count_from_mongo(mongo_host=transfer_data_info['mongo_host'],
                                                         mongo_port=transfer_data_info['mongo_port'],
                                                         db=transfer_data_info['mongo_db'],
                                                         collection=transfer_data_info['mongo_collection'],
                                                         query_params=query_params)
        es_count = es_client.count(index=transfer_data_info['elasticsearch_index'],
                                   doc_type=transfer_data_info['elasticsearch_doc_type'])['count']
    except Exception as e:
        current_app.logger.warning('Connected MongoDB or Elasticsearch occurred error.')
        current_app.logger.exception(e)
        return 'data: error\n\n'

    while True:
        increase_count = es_client.count(es_index=transfer_data_info['elasticsearch_index'],
                                         doc_type=transfer_data_info['elasticsearch_doc_type'])['count'] - es_count
        if increase_count >= transfer_volume:
            yield 'data: %s\n\n' % 100
            break
        percentage = increase_count / transfer_volume * 100
        yield 'data: %s\n\n' % percentage
        time.sleep(1)


@elasticsearch.route('/transfer/progress')
def transfer_progress():
    return Response(transfer_progress_event(), mimetype='text/event-stream')


@elasticsearch.route('/enable/transfer', methods=['POST'])
def enable_transfer():
    transfer_data_info = {}
    for k, v in request.form.items():
        transfer_data_info[k] = v
    transfer_data_info_queue.put(transfer_data_info)

    success, failed = es_client.transfer_data_from_mongo(index=request.form['elasticsearch_index'],
                                                         doc_type=request.form['elasticsearch_doc_type'],
                                                         use_mongo_id=request.form['use_mongo_id'],
                                                         indexed_flag_field_name=request.form['filter_field'],
                                                         mongo_host=request.form['mongo_host'],
                                                         mongo_port=request.form['mongo_port'],
                                                         mongo_db=request.form['mongo_db'],
                                                         mongo_collection=request.form['mongo_collection'])
    return jsonify({'success_count': success, 'fail_count': failed})


@elasticsearch.route('/enable/auto/transfer', methods=['POST'])
def enable_auto_transfer():
    if isinstance(request.form['interval'], int):
        interval = request.form['interval']
    else:
        interval = 60
    lock.acquire()
    try:
        global auto_transfer_thread_id
        global is_auto_transfer
        auto_transfer_thread_id = es_client.automatic_syn_data_from_mongo(index=request.form['elasticsearch_index'],
                                                                          doc_type=request.form[
                                                                              'elasticsearch_doc_type'],
                                                                          indexed_flag_field_name=request.form[
                                                                              'filter_field'],
                                                                          interval=interval,
                                                                          use_mongo_id=request.form['use_mongo_id'],
                                                                          mongo_host=request.form['mongo_host'],
                                                                          mongo_port=request.form['mongo_port'],
                                                                          mongo_db=request.form['mongo_db'],
                                                                          mongo_collection=request.form[
                                                                              'mongo_collection'])
        if not is_auto_transfer:
            is_auto_transfer = not is_auto_transfer
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({'status': 'failure'})
    finally:
        lock.release()
    return jsonify({'status': 'success'})


@elasticsearch.route('/cancel/auto/transfer', methods=['POST'])
def cancel_auto_transfer():
    lock.acquire()
    try:
        es_client.stop_automatic_syn_data(auto_transfer_thread_id)
        global is_auto_transfer
        if is_auto_transfer:
            is_auto_transfer = not is_auto_transfer
    except Exception:
        return jsonify({'status': 'failure'})
    finally:
        lock.release()
    return jsonify({'status': 'success'})


@elasticsearch.route('/cluster/health/', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_CLUSTER_HEALTH,
                          serializable_func=jsonify)
def cluster_health_info():
    return es_client.cluster_health()


@elasticsearch.route('/cluster/indices/health', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_CLUSTER_INDICES,
                          serializable_func=jsonify)
def indices_health():
    return es_client.cluster_health_for_indices()[1]


@elasticsearch.route('/cluster/stats', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_CLUSTER_STATS,
                          serializable_func=jsonify)
def cluster_stats():
    return es_client.cluster_status_info()


@elasticsearch.route('/nodes/stats/<node_id>', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_NODES_STATS,
                          serializable_func=jsonify)
def nodes_stats(node_id):
    return es_client.nodes_status_info(node_id=node_id)


@elasticsearch.route('/nodes/simple/info', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_NODES_SIMPLE_INFO,
                          serializable_func=jsonify)
def nodes_simple_info():
    return es_client.nodes_simple_info()


@elasticsearch.route('/indices/simple/info', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_INDICES_SIMPLE_INFO,
                          serializable_func=jsonify)
def indices_simple_info():
    return es_client.get_simple_info_for_index()


@elasticsearch.route('/indices/stats/<index>', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.ELASTICSEARCH_INDICES_STATS,
                          serializable_func=jsonify)
def indices_stats(index):
    return es_client.indices_stats_info(index=index.split(','))


@elasticsearch.route('/indices/close/<index>', methods=['POST'])
def close_index(index):
    return jsonify(es_client.close_index(index=index))


@elasticsearch.route('/indices/open/<index>', methods=['POST'])
def open_index(index):
    return jsonify(es_client.open_index(index=index))


@elasticsearch.route('/auto/transfer/status', methods=['GET'])
def auto_transfer_status():
    global is_auto_transfer
    return jsonify({'is_auto_transfer': is_auto_transfer})


@elasticsearch.route('/auto/transfer/status/change', methods=['GET'])
def change_auto_transfer_status():
    global is_auto_transfer
    lock.acquire()
    try:
        result = {'prev_status': is_auto_transfer, 'result': 'fail'}
        is_auto_transfer = not is_auto_transfer
        result['result'] = 'success'
    finally:
        lock.release()
    return jsonify(result)
