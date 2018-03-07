#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import threading
import time

from elasticsearch import Elasticsearch, helpers as es_helpers
from pymongo import MongoClient

from fish_core import default

lock = threading.Lock()

logger = logging.getLogger(__name__)


class ElasticsearchClient(object):
    """
    Class ElasticsearchClient represent a Elasticsearch client,
    it implement something feature base on elasticsearch.Elasticsearch.
    """

    automatic_syn_data_flag = {}
    automatic_thread_name_counter = 0

    def __init__(self):
        self.client = None

    def from_normal(self, hosts=default.ELASTICSEARCH_HOSTS, **kwargs):
        """
        Initialize a Elasticsearch client by specified hosts list.

        :param hosts: list of nodes we should connect to. Node should be a
            dictionary ({"host": "localhost", "port": 9200}), the entire dictionary
            will be passed to the :class:`~elasticsearch.Connection` class as
            kwargs, or a string in the format of ``host[:port]`` which will be
            translated to a dictionary automatically.  If no value is given the
            :class:`~elasticsearch.Urllib3HttpConnection` class defaults will be used

        :return: void
        """
        self.client = Elasticsearch(hosts=hosts, **kwargs)
        logger.info('Initialize normal Elasticsearch Client: %s.' % self.client)

    def from_sniffing(self,
                      active_nodes,
                      sniff_on_start=True,
                      sniff_on_connection_fail=True,
                      sniffer_timeout=60, **kwargs):
        """
        Initialize a Elasticsearch client for specify to sniff on startup to
        inspect the cluster and load balance across all nodes.
        The client can be configured to inspect the cluster state to get
        a list of nodes upon startup, periodically and/or on failure.

        :param active_nodes: the list of active nodes
        :param sniff_on_start: flag indicating whether to obtain a list of nodes
            from the cluser at startup time
        :param sniff_on_connection_fail: flag controlling if connection failure triggers a sniff
        :param sniffer_timeout: number of seconds between automatic sniffs
        :return: void
        """
        self.client = Elasticsearch(active_nodes,
                                    sniff_on_start=sniff_on_start,
                                    sniff_on_connection_fail=sniff_on_connection_fail,
                                    sniffer_timeout=sniffer_timeout, **kwargs)
        logger.info('Initialize sniffing Elasticsearch Client: %s.' % self.client)

    def from_ssl(self,
                 ca_certs,
                 client_cert,
                 client_key,
                 hosts=default.ELASTICSEARCH_HOSTS,
                 use_ssl=True,
                 verify_certs=True, **kwargs):
        """
        Initialize a Elasticsearch client by SSL.

        :param ca_certs: optional path to CA bundle. See
        https://urllib3.readthedocs.io/en/latest/security.html#using-certifi-with-urllib3
        :param client_cert: path to the file containing the private key and the
        certificate, or cert only if using client_key
        :param client_key: path to the file containing the private key if using
        separate cert and key files (client_cert will contain only the cert)
        :param hosts: hostname of the node
        :param use_ssl: use ssl for the connection if `True`
        :param verify_certs: whether to verify SSL certificates
        :return: void
        """
        self.client = Elasticsearch(hosts=hosts,
                                    use_ssl=use_ssl,
                                    verify_certs=verify_certs,
                                    ca_certs=ca_certs,
                                    client_cert=client_cert,
                                    client_key=client_key, **kwargs)
        logger.info('Initialize SSL Elasticsearch Client: %s.' % self.client)

    def transfer_data_from_mongo(self,
                                 index,
                                 doc_type,
                                 use_mongo_id=False,
                                 indexed_flag_field_name='',
                                 mongo_query_params={},
                                 mongo_host=default.MONGO_HOST,
                                 mongo_port=default.MONGO_PORT,
                                 mongo_db=default.MONGO_DB,
                                 mongo_collection=default.MONGO_COLLECTION):
        """
        Transfer data from MongoDB into the Elasticsearch, the hostname, port, database and
        collection name in MongoDB default from load in default.py

        :param index: The name of the index
        :param doc_type: The type of the document
        :param use_mongo_id: Use id of MongoDB in the Elasticsearch if is true otherwise automatic generation
        :param indexed_flag_field_name: the name of the field of the document,
                    if associated value is False will synchronize data for it
        :param mongo_client_params: The dictionary for client params of MongoDB
        :param mongo_query_params: The dictionary for query params of MongoDB
        :param mongo_host: The name of the hostname from MongoDB
        :param mongo_port: The number of the port from MongoDB
        :param mongo_db: The name of the database from MongoDB
        :param mongo_collection: The name of the collection from MongoDB
        :return: void
        """
        mongo_client = MongoClient(host=mongo_host, port=int(mongo_port))
        try:
            collection = mongo_client[mongo_db][mongo_collection]
            if indexed_flag_field_name != '':
                mongo_query_params.update({indexed_flag_field_name: False})
            mongo_docs = collection.find(mongo_query_params)
        finally:
            mongo_client.close()
        # Joint actions of Elasticsearch for execute bulk api
        actions = []
        id_array = []
        for doc in mongo_docs:
            action = {
                '_op_type': 'index',
                '_index': index,
                '_type': doc_type
            }
            id_array.append(doc['_id'])
            if not use_mongo_id:
                doc.pop('_id')
            else:
                doc['id'] = str(doc['_id'])
                doc.pop('_id')
            action['_source'] = doc
            actions.append(action)
        success, failed = es_helpers.bulk(self.client, actions, request_timeout=60 * 60)
        logger.info(
            'Transfer data from MongoDB(%s:%s) into the Elasticsearch(%s) success: %s, failed: %s' % (
                mongo_host, mongo_port, self.client, success, failed))

        # Back update flag
        if indexed_flag_field_name != '':
            t = threading.Thread(target=ElasticsearchClient._back_update_mongo,
                                 args=(self, mongo_host, mongo_port, mongo_db, mongo_collection, id_array,
                                       {indexed_flag_field_name: True}),
                                 name='mongodb_back_update')
            t.start()
        return success, failed

    def _back_update_mongo(self,
                           mongo_host, mongo_port,
                           mongo_db,
                           mongo_collection,
                           id_array, update):
        client = MongoClient(host=mongo_host, port=mongo_port)
        try:
            collection = client[mongo_db][mongo_collection]
            for id in id_array:
                collection.update({'_id': id}, {'$set': update})
        finally:
            client.close()

    def create(self, index, doc_type, id, body, params={}, **kwargs):
        result = self.client.create(index, doc_type, id, body, params=params, **kwargs)
        logger.info(
            'Create[index: %s, doc type: %s, id: %s] is done body: \n %s' % (index, doc_type, id, body))
        logger.debug('<Verbose message> operation: %s, version: %s shards: %s' % (
            result['result'], result['_version'], result['_shards']))
        return result

    def index(self, index, doc_type, body, id=None, params={}, **kwargs):
        result = self.client.index(index, doc_type, body, id, params=params, **kwargs)
        if id is None:
            id_message = 'Automatic Generation'
        else:
            id_message = id
        logger.info(
            'Index[index: %s, doc type: %s, id: %s] is done body: \n %s' % (index, doc_type, id_message, body))
        logger.debug('<Verbose message> operation: %s version: %s shards: %s' % (
            result['result'], result['_version'], result['_shards']))
        return result

    def delete(self, index, doc_type, id, params={}, **kwargs):
        result = self.client.delete(index, doc_type, id, params=params, **kwargs)
        logger.info(
            'Delete[index: %s, doc type: %s, id: %s] is done' % (index, doc_type, id))
        logger.debug('<Verbose message> operation: %s version: %s shards: %s' % (
            result['result'], result['_version'], result['_shards']))
        return result

    def search(self, index=None, doc_type=None, body=None, params={}, **kwargs):
        result = self.client.search(index, doc_type, body, params=params, **kwargs)
        if index is None and doc_type is None and body is None:
            logger.info('Search[all mode] is done')
            return result
        logger.info(
            'Search[index: %s, doc type: %s] is done body: \n %s' % (index, doc_type, body))
        logger.debug(
            '<Verbose message> took: %s shards: %s hits: %s' % (
                result['took'], result['_shards'], result['hits']['total']))
        return result

    def count(self, index=None, doc_type=None, body=None, params={}, **kwargs):
        result = self.client.count(index, doc_type, body, params=params, **kwargs)
        if index is None and doc_type is None and body is None:
            logger.info('Count[all mode] is done')
            return result
        logger.info('Count[index: %s, doc type: %s] is done body: \n %s' % (index, doc_type, body))
        logger.debug('<Verbose message> count: %s shards: %s' % (result['count'], result['_shards']))
        return result

    def update(self, index, doc_type, id, body=None, params={}, **kwargs):
        result = self.client.update(index, doc_type, id, body, params=params, **kwargs)
        logger.info(
            'Update[index: %s, doc type: %s, id: %s] is done body: \n %s' % (index, doc_type, id, body))
        logger.debug('<Verbose message> operation: %s version: %s shards: %s' % (
            result['result'], result['_version'], result['_shards']))
        return result

    def bulk(self, actions, stats_only=False, **kwargs):
        """
        Executes bulk api by elasticsearch.helpers.bulk.

        :param actions: iterator containing the actions
        :param stats_only:if `True` only report number of successful/failed
        operations instead of just number of successful and a list of error responses
        Any additional keyword arguments will be passed to
        :func:`~elasticsearch.helpers.streaming_bulk` which is used to execute
        the operation, see :func:`~elasticsearch.helpers.streaming_bulk` for more
        accepted parameters.
        """
        success, failed = es_helpers.bulk(self.client, actions, stats_only, **kwargs)
        logger.info('Bulk is done success %s failed %s actions: \n %s' % (success, failed, actions))

    def mget(self, body, index=None, doc_type=None, params={}, **kwargs):
        result = self.client.mget(body, index, doc_type, params=params, **kwargs)
        logger.info('Mget[index: %s, doc type: %s] is done body: \n %s' % (index, doc_type, body))
        return result

    def get_client(self):
        if self.client is None:
            logger.warning('Elasticsearch Client is None')
        return self.client

    # TODO: Use more effective solution
    def automatic_syn_data_from_mongo(self,
                                      index,
                                      doc_type,
                                      indexed_flag_field_name,
                                      thread_name='automatic_syn_data_thread',
                                      interval=60,
                                      use_mongo_id=False,
                                      mongo_query_params={},
                                      mongo_host=default.MONGO_HOST,
                                      mongo_port=default.MONGO_PORT,
                                      mongo_db=default.MONGO_DB,
                                      mongo_collection=default.MONGO_COLLECTION):
        """
        Automatic synchronize data that from MongoDB into the Elasticsearch by schedule task,
        it will synchronize this data if the indexed_flag_field_name of the field of the document is False.
        Noteworthy that the function may be no good please you caution use it.

        :param indexed_flag_field_name: the name of the field of the document,
                    if associated value is False will synchronize data for it
        :param thread_name: the name of the schedule task thread
        :param interval: the time that executes interval of the scheduled task every time (unit second)
        :return: the thread id, you can use this id to cancel associated task
        """
        thread_id = self._generate_thread_id(thread_name)
        if thread_id in ElasticsearchClient.automatic_syn_data_flag:
            lock.acquire()
            try:
                thread_name = thread_name + '-%s' % ElasticsearchClient.automatic_thread_name_counter
                ElasticsearchClient.automatic_thread_name_counter += 1
                thread_id = self._generate_thread_id(thread_name)
            finally:
                lock.release()
        ElasticsearchClient.automatic_syn_data_flag[thread_id] = True

        t = threading.Thread(target=ElasticsearchClient._automatic_syn_data_from_mongo_worker,
                             args=(self, thread_id, index, doc_type,
                                   indexed_flag_field_name, interval, use_mongo_id,
                                   mongo_query_params,
                                   mongo_host, mongo_port,
                                   mongo_db, mongo_collection),
                             name=thread_name)

        t.start()
        return thread_id

    def _generate_thread_id(self, thread_name):
        return str(hash(thread_name))

    def stop_automatic_syn_data(self, thread_id):
        lock.acquire()
        try:
            ElasticsearchClient.automatic_syn_data_flag[thread_id] = False
        finally:
            lock.release()

    def _automatic_syn_data_from_mongo_worker(self,
                                              thread_id,
                                              index,
                                              doc_type,
                                              indexed_flag_field_name,
                                              interval=60,
                                              use_mongo_id=False,
                                              mongo_query_params={},
                                              mongo_host=default.MONGO_HOST,
                                              mongo_port=default.MONGO_PORT,
                                              mongo_db=default.MONGO_DB,
                                              mongo_collection=default.MONGO_COLLECTION):
        current_thread__name = threading.current_thread().name
        while ElasticsearchClient.automatic_syn_data_flag[thread_id]:
            logger.info('[%s]: synchronize data work start %s:%s -----> %s' % (
                current_thread__name, mongo_host, mongo_port, self.client))
            success, failed = self.transfer_data_from_mongo(index=index, doc_type=doc_type,
                                                            use_mongo_id=use_mongo_id,
                                                            indexed_flag_field_name=indexed_flag_field_name,
                                                            mongo_query_params=mongo_query_params,
                                                            mongo_host=mongo_host, mongo_port=mongo_port,
                                                            mongo_db=mongo_db, mongo_collection=mongo_collection)
            logger.info('[%s]: synchronize data work done %s:%s -----> %s [success=%s, failed=%s]' % (
                current_thread__name, mongo_host, mongo_port, self.client, success, failed))
            time.sleep(interval)
        logger.info('[%s]: synchronize data work is shutdown ' % current_thread__name)

    def open_index(self, index, params={}, **kwargs):
        result = self.client.indices.open(index, params=params, **kwargs)
        logger.info('Index %s is opened' % index)
        return result

    def close_index(self, index, params={}, **kwargs):
        result = self.client.indices.close(index, params=params, **kwargs)
        logger.info('Index %s is closed' % index)
        return result

    def indices_stats_info(self, index=None, metric=None, params={}, **kwargs):
        result = self.client.indices.stats(index=index, metric=metric, params=params, **kwargs)
        logger.info('Acquire indices status information is done')
        return result

    def get_simple_info_for_index(self, index=None, params={}, **kwargs):
        """
        Return a list of simple info by specified index (default all), each elements is a dictionary
        such as
        {
            'health' : 'green', 'status' : 'open',
            'index' : 'xxxx', 'uuid' : 'xxxx',
            'pri' : 1, 'rep' : 1,
            `docs_count` : 4, 'docs_deleted' : 0,
            'store_size' : 10kb, 'pri_store_size' : 10kb
        }
        """
        raw = self.client.cat.indices(index, params=params, **kwargs).split('\n')
        list = []
        for r in raw:
            alter = r.split(' ')
            if len(alter) < 10: continue
            dict = {
                'health': alter[0],
                'status': alter[1],
                'index': alter[2],
            }
            if len(alter) == 11:
                # May appear split fail (alter[3] is a empty string)
                dict['uuid'] = alter[4]
                i = 5
            else:
                dict['uuid'] = alter[3]
                i = 4
            dict['pri'] = alter[i]
            i += 1
            dict['rep'] = alter[i]
            i += 1
            dict['docs_count'] = alter[i]
            i += 1
            dict['docs_deleted'] = alter[i]
            i += 1
            dict['store_size'] = alter[i]
            i += 1
            dict['pri_store_size'] = alter[i]
            list.append(dict)
        logger.info('Acquire simple information of the index is done succeeded: %s' % len(list))
        return list

    def cluster_health(self, index=None, params={}, **kwargs):
        result = self.client.cluster.health(index, params=params, **kwargs)
        message = 'Acquire cluster health information is done index: %s'
        if index is None:
            message = message % 'all'
        else:
            message = message % index
        logger.info(message)
        return result

    def cluster_health_for_indices(self, index=None, params={}, **kwargs):
        """
        Return a list of cluster health of specified indices(default all),
        the first element is a dictionary represent a global information of the cluster
        such as "cluster_name", "number_of_nodes"...
        the second element represent a indices information list that each element is a dictionary for one index
        such as [{'index' : 'a', 'status' : 'yellow', ...} , {'index' : 'b', 'status' : 'yellow', ...}, ....]
        """
        params['level'] = 'indices'
        result = self.cluster_health(index, params, **kwargs)
        return self._process_cluster_health_info(result)

    def cluster_health_for_shards(self, index=None, params={}, **kwargs):
        """
        Return a list of cluster health of specified indices(default all) and
        append shards information of each index
        the first element is a dictionary represent a global information of the cluster
        the second element represent a information of indices and its shards and each element is a dictionary
        such as [{'index' : 'a', 'status' : 'yellow', ..., 'shards' : {'0' : {...}, '1' : {...}, ...}, ...]
        """
        params['level'] = 'shards'
        result = self.cluster_health(index, params, **kwargs)
        return self._process_cluster_health_info(result)

    def cluster_status_info(self, node_id=None, params={}, **kwargs):
        result = self.client.cluster.stats(node_id=node_id, params=params, **kwargs)
        logger.info('Acquire cluster status information is done')
        return result

    def _process_cluster_health_info(self, info):
        list = []
        first = {}
        second = []
        for k, v in info.items():
            if k == 'indices':
                for k2, v2 in v.items():
                    index = {}
                    index['index'] = k2
                    index.update(v2)
                    second.append(index)
            else:
                first[k] = v
        list.append(first)
        list.append(second)
        return list

    def nodes_status_info(self, node_id=None, metric=None, index_metric=None, params={}, **kwargs):
        result = self.client.nodes.stats(node_id=node_id, metric=metric, index_metric=index_metric, params=params,
                                         **kwargs)
        logger.info('Acquire nodes status information is done')
        return result

    def nodes_info(self, node_id=None, metric=None, params={}, **kwargs):
        result = self.client.nodes.info(node_id=node_id, metric=metric, params=params, **kwargs)
        logger.info('Acquire nodes info is done')
        return result

    def nodes_simple_info(self, params={}, **kwargs):
        """
        Return a dictionary of the nodes simple info that key is a column name,
        such as [{"http_address": "192.111.111.111", "name" : "test", ...}, ...]
        """
        h = ['name', 'pid', 'http_address', 'version', 'jdk', 'disk.total', 'disk.used_percent', 'heap.current',
             'heap.percent', 'ram.current', 'ram.percent', 'uptime', 'node.role']
        result = self.client.cat.nodes(v=True, h=h, **kwargs, params=params)
        result = [x.strip().split(' ') for x in result.split('\n')]
        # Clean up the space
        result.remove(result[-1])
        for i in range(len(result)):
            result[i] = list(filter(lambda x: x != '', result[i]))
        # Packing into the dictionary
        dicts = []
        for i in range(len(result) - 1):
            dict = {}
            for k, v in zip(result[0], result[i + 1]):
                dict[k] = v
            dicts.append(dict)

        logger.info('Acquire simple information of the nodes is done succeeded: %s' % len(dicts))
        return dicts


def get_documents_count_from_mongo(db,
                                   collection,
                                   query_params={},
                                   mongo_host=default.MONGO_HOST,
                                   mongo_port=default.MONGO_PORT):
    client = MongoClient(host=mongo_host, port=mongo_port)
    try:
        result = client[db][collection].count(query_params)
        logger.info('Acquire documents count from MongoDB is done, result: %s' % result)
    finally:
        client.close()
    return result


def create_multiple_queries_statement(condition='should'):
    """
    >>> create_multiple_queries_statement()
    {'query': {'bool': {'should': []}}}
    >>> create_multiple_queries_statement(condition='must')
    {'query': {'bool': {'must': []}}}
    """
    return {'query': {'bool': {condition: []}}}


def create_query_statement(condition='match'):
    """
    >>> create_query_statement()
    {'query': {'match': {}}}
    >>> create_query_statement(condition='bool')
    {'query': {'bool': {}}}
    """
    return {'query': {condition: {}}}


def append_condition(statement, condition, key, value):
    """
    >>> list = []
    >>> append_condition(list, 'match', 'name', 'Jack')
    >>> list
    [{'match': {'name': 'Jack'}}]
    >>> dict = {}
    >>> append_condition(dict, 'match', 'name', 'Marry')
    >>> dict
    {'match': {'name': 'Marry'}}
    """
    if isinstance(statement, list):
        statement.append({condition: {key: value}})
    if isinstance(statement, dict):
        statement[condition] = {key: value}
