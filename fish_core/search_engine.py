# !/usr/bin/python
# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from fish_core import default
import logging


class ElasticsearchClient(object):
    """
    Class ElasticsearchClient represent a Elasticsearch client,
    it implement something feature base on elasticsearch.Elasticsearch.
    """

    def __init__(self):
        self.client = None
        self.logger = logging.getLogger(__class__.__name__)

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
        self.logger.debug("Initialize normal Elasticsearch Client by %s." % hosts)

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
        self.logger.debug("Initialize sniffing Elasticsearch Client by %s." % active_nodes)

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
        self.logger.debug("Initialize SSL Elasticsearch Client by %s." % hosts)
