from werkzeug.contrib.cache import SimpleCache
import logging

logger = logging.getLogger(__name__)


class CacheKeys():
    SCRAPYD_STATUS_KEY = 'scrapyd_status'
    SCRAPYD_JOB_LIST = 'scrapyd_job_list'
    SCRAPYD_LOGS_INFO = 'scrapyd_logs_info'
    SCRAPYD_PROJECT_LIST = 'scrapyd_project_list'
    SCRAPYD_SPIDER_LIST = 'scrapyd_spider_list'
    ELASTICSEARCH_CLUSTER_HEALTH = 'elasticsearch_cluster_health'


class CacheStrategy():
    SIMPLE = 'simple'


def is_cacheable(current_app, cache_key):
    return current_app.config['ENABLE_CACHE'] and current_app.config['GLOBAL_CACHE'].get(cache_key) is not None


def set_cached(current_app, cache_key, data):
    if current_app.config['ENABLE_CACHE']:
        current_app.config['GLOBAL_CACHE'].set(cache_key, data,
                                               timeout=current_app.config['CACHE_EXPIRE'])


def get_cached(current_app, cache_key):
    return current_app.config['GLOBAL_CACHE'].get(cache_key)


def initialize_cache(app, strategy=CacheStrategy.SIMPLE):
    if app.config['ENABLE_CACHE']:
        if strategy == CacheStrategy.SIMPLE:
            app.config['GLOBAL_CACHE'] = SimpleCache()
        logger.info('Initialize global cache completion strategy: %s' % strategy)
    else:
        logger.info('Initialize global cache failure, current configuration does not support cache')
