# !/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import threading
import time

from elasticsearch import Elasticsearch, helpers as es_helpers
from pymongo import MongoClient

from fish_core import default

lock = threading.Lock()


class ElasticsearchClient(object):
    """
    Class ElasticsearchClient represent a Elasticsearch client,
    it implement something feature base on elasticsearch.Elasticsearch.
    """

    automatic_syn_data_flag = {}
    automatic_thread_name_counter = 0

    def __init__(self):
        self.client = None
        self.logger = logging.getLogger(__name__)

    def from_normal(self, hosts=default.ELASTICSEARCH_HOSTS):
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
        self.client = Elasticsearch(hosts=hosts)
        self.logger.info('Initialize normal Elasticsearch Client: %s.' % self.client)

    def from_sniffing(self,
                      active_nodes,
                      sniff_on_start=True,
                      sniff_on_connection_fail=True,
                      sniffer_timeout=60):
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
                                    sniffer_timeout=sniffer_timeout)
        self.logger.info('Initialize sniffing Elasticsearch Client: %s.' % self.client)

    def from_ssl(self,
                 ca_certs,
                 client_cert,
                 client_key,
                 hosts=default.ELASTICSEARCH_HOSTS,
                 use_ssl=True,
                 verify_certs=True):
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
                                    client_key=client_key)
        self.logger.info('Initialize SSL Elasticsearch Client: %s.' % self.client)

    def transfer_data_from_mongo(self,
                                 index,
                                 doc_type,
                                 use_mongo_id=False,
                                 mongo_client_params=None,
                                 mongo_query_params=None,
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
        :param mongo_client_params: The dictionary for client params of MongoDB
        :param mongo_query_params: The dictionary for query params of MongoDB
        :param mongo_host: The name of the hostname from MongoDB
        :param mongo_port: The number of the port from MongoDB
        :param mongo_db: The name of the database from MongoDB
        :param mongo_collection: The name of the collection from MongoDB
        :return: void
        """
        mongo_client = MongoClient(mongo_client_params, host=mongo_host, port=mongo_port)
        collection = mongo_client[mongo_db][mongo_collection]
        if use_mongo_id:
            mongo_docs = collection.find(mongo_query_params)
        else:
            mongo_docs = collection.find(mongo_query_params, projection={'_id': False})
        # Joint actions of Elasticsearch for execute bulk api
        actions = []
        for doc in mongo_docs:
            action = {
                '_op_type': 'index',
                '_index': index,
                '_type': doc_type
            }
            if '_id' in doc:
                action['_id'] = doc['_id']
                doc.pop('_id')
            action['_source'] = doc
            actions.append(action)
        success, failed = es_helpers.bulk(self.client, actions)
        mongo_client.close()
        self.logger.info(
            'Transfer data from MongoDB(%s:%s) into the Elasticsearch(%s) success: %s, failed: %s' % (
                mongo_host, mongo_port, self.client, success, failed))

    # TODO: Use more effective solution
    def automatic_syn_data_from_mongo(self,
                                      index,
                                      doc_type,
                                      indexed_flag_field_name,
                                      thread_name='automatic_syn_data_thread',
                                      interval=60,
                                      use_mongo_id=False,
                                      mongo_client_params=None,
                                      mongo_query_params=None,
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
                                   mongo_client_params, mongo_query_params,
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
                                              mongo_client_params=None,
                                              mongo_query_params=None,
                                              mongo_host=default.MONGO_HOST,
                                              mongo_port=default.MONGO_PORT,
                                              mongo_db=default.MONGO_DB,
                                              mongo_collection=default.MONGO_COLLECTION):
        current_thread__name = threading.current_thread().name
        while ElasticsearchClient.automatic_syn_data_flag[thread_id]:
            self.logger.info('[%s]: synchronize data work start %s:%s -----> %s' % (
                current_thread__name, mongo_host, mongo_port, self.client))
            self.transfer_data_from_mongo(index, doc_type,
                                          use_mongo_id, mongo_client_params,
                                          mongo_query_params=mongo_query_params.update(
                                              {indexed_flag_field_name: False}),
                                          mongo_host=mongo_host, mongo_port=mongo_port,
                                          mongo_db=mongo_db, mongo_collection=mongo_collection)
            self.logger.info('[%s]: synchronize data work done %s:%s -----> %s' % (
                current_thread__name, mongo_host, mongo_port, self.client))
            time.sleep(interval)
        self.logger.info('[%s]: synchronize data work is shutdown ' % current_thread__name)
