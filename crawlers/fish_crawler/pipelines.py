# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem
from twisted.internet.threads import deferToThread

from fish_utils.simhash import Simhash
from scrapy_redis import connection

# TODO: Will the default configuration variable into the independent module file
default_host = 'localhost'
default_port = 27017
default_db_name = '%(spider)s'
default_collection_name = '%(spider)s:items'
default_simhash_key = '%(spider)s:simhash_set'


class MongodbPipeline(object):
    """
    Push serialized item into the mongodb.
    """

    def __init__(self,
                 url,
                 host=default_host,
                 port=default_port,
                 db_name=default_db_name,
                 collection_name=default_collection_name
                 ):
        """
        :param url: specify mongodb url for connect.
        :param host: host name of the mongodb.
        :param port: port of the mongodb.
        :param db_name: specify database name.
        :param collection_name: where to store items.
        """
        if url is None:
            self.url = ""
        else:
            self.url = url
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name

    def open_spider(self, spider):
        """
        Initialize Mongodb client.
        """
        if self.url == "":
            self.client = pymongo.MongoClient(self.host, self.port)
        else:
            self.client = pymongo.MongoClient(self.url)

        self.db_name, self.collection_name = self._replace_placeholder(spider)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    def _replace_placeholder(self, spider):
        """
        Returns replaced db_name and collection_name(base on spider's name).
        if your db_name or collection_name does not have a placeholder or
        your db_name or collection_name that not base on spider's name
        you must override this function.
        """
        return self.db_name % {'spider': spider.name}, self.collection_name % {'spider': spider.name}

    @classmethod
    def from_settings(cls, settings):
        params = {}
        if settings.get('MONGODB_URL'):
            params['url'] = settings['MONGODB_URL']
        if settings.get('MONGODB_HOST'):
            params['host'] = settings['MONGODB_HOST']
        if settings.get('MONGODB_PORT'):
            params['port'] = settings['MONGODB_PORT']
        if settings.get('MONGODB_DB_NAME'):
            params['db_name'] = settings['MONGODB_DB_NAME']
        if settings.get('MONGODB_COLLECTION_NAME'):
            params['collection_name'] = settings['MONGODB_COLLECTION_NAME']

        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item_thread, item)

    def _process_item_thread(self, item):
        self.db[self.collection_name].insert_one(dict(item))
        return item


class DuplicatesPipeline(object):
    """
    Validate item similarity by simhash and reject item that similarity greater than specify a limit.
    Default use the same address as the redis queue.
    """

    def __init__(self, client, key=default_simhash_key):
        self.client = client
        self.key = key

    @classmethod
    def from_settings(cls, settings):
        params = {
            'client': connection.from_settings(settings),
        }
        if settings.get('REDIS_SIMHASH_KEY'):
            params['key'] = settings['REDIS_SIMHASH_KEY']

        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    # TODO: Alter to be method for more efficient
    def process_item(self, item, spider):
        self.key = self.key % {'spider': spider.name}
        item_simhash = item['simhash']

        if self.client.sismember(self.key, item_simhash):
            raise DropItem("Duplicate item found: %s" % item)
        else:
            simhash = Simhash(item_simhash)
            for other in self.client.smembers(self.key):
                if simhash.is_equal(other):
                    raise DropItem("Similarity high of the item: %s" % item)

        self.client.sadd(self.key, item_simhash)
        return item
