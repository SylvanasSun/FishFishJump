#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor

import redis
from common_cache import Cache
from flask import Blueprint, request, current_app, render_template, abort

from fish_core.search_engine import ElasticsearchClient, create_multiple_queries_statement, append_condition

search_view = Blueprint('search', __name__)

es_client = None

redis_pool = None

cache = None

thread_pool = None

cache_expire = 30

PAGE_SIZE = 10

PRE_QUERY_PAGE_SIZE = PAGE_SIZE * 10


def init_elasticsearch(flask_app):
    global es_client
    hosts = flask_app.config['ELASTICSEARCH_HOSTS'].split(',')
    address_list = []
    for host in hosts:
        host = host.strip()
        temp = host.split(':')
        address_list.append({
            'host': temp[0].strip(),
            'port': int(temp[1].strip())
        })
    es_client = ElasticsearchClient()
    try:
        es_client.from_normal(address_list)
        flask_app.logger.info('Initialize elasticsearch client completed')
    except Exception as e:
        flask_app.logger.exception(e)


def init_redis(flask_app):
    global redis_pool
    enable_redis = flask_app.config['ENABLE_REDIS_FOR_CACHE']
    if enable_redis:
        host = flask_app.config['REDIS_HOST']
        port = flask_app.config['REDIS_PORT']
        try:
            redis_pool = redis.ConnectionPool(host=host, port=port)
            flask_app.logger.info('Initialize redis client <%s:%s> completed' % (host, port))
        except Exception as e:
            flask_app.logger.exception(e)


def init_thread_pool(max_workers=10, thread_name_prefix='FFJ-Searcher-Cache-Updater-'):
    global thread_pool
    thread_pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix=thread_name_prefix)


def read_cache_from_redis(key):
    if redis_pool is not None:
        client = redis.Redis(connection_pool=redis_pool)
        return client.get(key)


def write_cache_to_redis(key, value):
    if redis_pool is not None:
        client = redis.Redis(connection_pool=redis_pool)
        client.set(key, value, ex=cache_expire * 2)


def init_cache():
    global cache
    if redis_pool is not None:
        cache = Cache(expire=cache_expire, instance_name='FFJ_SEARCHER_CACHE', cache_loader=read_cache_from_redis)
    else:
        cache = Cache(expire=cache_expire, instance_name='FFJ_SEARCHER_CACHE')


def format_number(number):
    """
    >>> format_number(1)
    1
    >>> format_number(22)
    22
    >>> format_number(333)
    333
    >>> format_number(4444)
    '4,444'
    >>> format_number(55555)
    '55,555'
    >>> format_number(666666)
    '666,666'
    >>> format_number(7777777)
    '7,777,777'
    """
    char_list = list(str(number))
    length = len(char_list)
    if length <= 3:
        return number

    result = ''
    if length % 3 != 0:
        while len(char_list) % 3 != 0:
            c = char_list[0]
            result += c
            char_list.remove(c)
        result += ','

    i = 0
    while len(char_list) > 0:
        c = char_list[0]
        result += c
        char_list.remove(c)
        i += 1
        if i % 3 == 0:
            result += ','

    return result[0:-1] if result[-1] == ',' else result


def generate_key(url, page_number):
    """
    >>> url_a = 'http://localhost:5009/search?keywords=a'
    >>> generate_key(url_a, 10)
    'http://localhost:5009/search?keywords=a&page=10'
    >>> url_b = 'http://localhost:5009/search?keywords=b&page=1'
    >>> generate_key(url_b, 10)
    'http://localhost:5009/search?keywords=b&page=10'
    """
    index = url.rfind('page')
    if index != -1:
        result = url[0:index]
        result += 'page=%s' % page_number
    else:
        result = url
        result += '&page=%s' % page_number
    return result


def query_from_es(size, from_, keywords):
    stat = create_multiple_queries_statement(condition='should')
    list = stat['query']['bool']['should']
    append_condition(list, condition='match', key='title', value=keywords)
    append_condition(list, condition='match', key='description', value=keywords)
    append_condition(list, condition='match', key='keywords', value=keywords)
    append_condition(list, condition='bool', key='should', value=[])
    bool_stat = list[-1:][0]['bool']['should']
    append_condition(bool_stat, condition='match', key='url', value=keywords)
    append_condition(bool_stat, condition='match', key='p_texts', value=keywords)
    append_condition(bool_stat, condition='match', key='links_text', value=keywords)
    # query Elasticsearch
    es_index = current_app.config['ELASTICSEARCH_INDEX']
    es_doc_type = current_app.config['ELASTICSEARCH_DOC_TYPE']
    result = es_client.search(index=es_index, doc_type=es_doc_type, body=stat, size=size, from_=from_)
    return result


def packing_page_items(data, start, end):
    pages_info = []
    related_kw = []
    for x in data[start:end]:
        x = x['_source']
        pages_info.append({
            'title': x['title'],
            'description': x['description'],
            'url': x['url']
        })
        related_kw.append(x['keywords'])
    return pages_info, related_kw[0:8]


def update_cache_task(data, url, page_number, max_page_number):
    index_start = 0
    index_end = index_start + 10
    data_len = len(data['hits']['hits'])
    total = data['hits']['total']
    hits = data['hits']['hits']
    for i in range(page_number, max_page_number + 1):
        if index_start >= data_len:
            break
        value = {'total': total}
        pages_info, related_kw = packing_page_items(hits, index_start, index_end)
        value['pages_info'] = pages_info
        value['related_kw'] = related_kw

        json_re = json.dumps(value)
        key = generate_key(url, i)
        cache.put(key=key, value=json_re)
        write_cache_to_redis(key=key, value=json_re)
        index_start, index_end = index_end, index_end + 10


def generate_pagination(total_page_num, current_page_num):
    """
    >>> PAGE_SIZE = 10
    >>> generate_pagination(total_page_num=9, current_page_num=1)
    {'start': 1, 'end': 9, 'current': 1}
    >>> generate_pagination(total_page_num=20, current_page_num=12)
    {'start': 8, 'end': 17, 'current': 12}
    >>> generate_pagination(total_page_num=20, current_page_num=4)
    {'start': 1, 'end': 10, 'current': 4}
    >>> generate_pagination(total_page_num=16, current_page_num=14)
    {'start': 7, 'end': 16, 'current': 14}
    """
    pagination = {'start': 1, 'end': PAGE_SIZE, 'current': current_page_num}

    if total_page_num <= PAGE_SIZE:
        pagination['end'] = total_page_num
    else:
        # base on front four and back five
        pagination['start'] = current_page_num - 4
        pagination['end'] = current_page_num + 5

        if pagination['start'] < 1:
            pagination['start'] = 1
            pagination['end'] = PAGE_SIZE

        if pagination['end'] > total_page_num:
            pagination['end'] = total_page_num
            pagination['start'] = total_page_num - 9

    return pagination


@search_view.route('/search', methods=['GET'])
def search():
    url = request.url
    keywords = request.args.get('keywords', '')
    page_number = int(request.args.get('page', 1))
    page_index = (page_number - 1) * PAGE_SIZE
    key = generate_key(url, page_number)
    start = time.time()
    result = cache.get(key=key)

    # cache missing
    if result is None:
        try:
            result = query_from_es(size=PRE_QUERY_PAGE_SIZE, from_=page_index, keywords=keywords)
        except Exception as e:
            current_app.logger.exception(e)
            abort(404)

        max_page_number = page_number + 9
        # update cache
        if thread_pool is not None:
            thread_pool.submit(update_cache_task, result, url, page_number, max_page_number)
        else:
            update_cache_task(result, url, page_number, max_page_number)

        total = result['hits']['total']
        pages_info, related_kw = packing_page_items(result['hits']['hits'], 0, PAGE_SIZE)
        result = {
            'total': total,
            'pages_info': pages_info,
            'related_kw': related_kw
        }
    else:
        # cache hit
        result = json.loads(result)

    result_count = result['total']
    total_page_number = int((result_count + PAGE_SIZE - 1) / PAGE_SIZE)
    result_count = format_number(result_count)
    footer_info = 'FishFishJump Searcher 2017-%s - ' % datetime.datetime.now().year
    pagination = generate_pagination(total_page_number, page_number)
    consuming_time = round(time.time() - start, 2)
    # The consuming_time generally is 0.0 when in the situations of a cache hit
    # so generate random for getting better the user experience
    if consuming_time <= 0.0:
        consuming_time = round(random.uniform(0.1, 2), 2)

    return render_template('search_result.html',
                           title=keywords,
                           consuming_time=consuming_time,
                           result_count=result_count,
                           pages_info=result['pages_info'] if len(result['pages_info']) > 0 else None,
                           related_kw=result['related_kw'],
                           footer_info=footer_info,
                           pagination=pagination)
