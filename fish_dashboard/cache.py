import logging
import json
import functools
from werkzeug.contrib.cache import SimpleCache

logger = logging.getLogger(__name__)

GLOBAL_CACHE = 'GLOBAL_CACHE'

CACHE_EXPIRE = 'CACHE_EXPIRE'


class CacheKeys():
    SCRAPYD_STATUS_KEY = 'scrapyd_status'
    SCRAPYD_JOB_LIST = 'scrapyd_job_list'
    SCRAPYD_LOGS_INFO = 'scrapyd_logs_info'
    SCRAPYD_PROJECT_LIST = 'scrapyd_project_list'
    SCRAPYD_SPIDER_LIST = 'scrapyd_spider_list'
    ELASTICSEARCH_CLUSTER_HEALTH = 'elasticsearch_cluster_health'
    ELASTICSEARCH_CLUSTER_INDICES = 'elasticsearch_cluster_indices'


class CacheStrategy():
    SIMPLE = 'simple'


def is_cacheable(current_app, cache_key):
    return current_app.config[GLOBAL_CACHE].get(cache_key) is not None


def set_cached(current_app, cache_key, data):
    current_app.config[GLOBAL_CACHE].set(cache_key, data,
                                         timeout=current_app.config[CACHE_EXPIRE])


def get_cached(current_app, cache_key):
    return current_app.config[GLOBAL_CACHE].get(cache_key)


def initialize_cache(app, strategy=CacheStrategy.SIMPLE):
    if strategy == CacheStrategy.SIMPLE:
        app.config[GLOBAL_CACHE] = SimpleCache()
    logger.info('Initialize global cache completion strategy: %s' % strategy)


def cache(flask_app, key, serializable_func=json.dumps):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if is_cacheable(flask_app, key):
                logger.info('Hit the cache %s and return data in the cache' % key)
                return serializable_func(get_cached(flask_app, key))
            result = func(*args, **kw)
            set_cached(flask_app, key, result)
            return serializable_func(result)

        return wrapper

    return decorator
