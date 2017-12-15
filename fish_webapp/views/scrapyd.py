from flask import Blueprint, jsonify, current_app
from scrapyd.scrapyd_agent import ScrapydAgent
from scrapyd.scrapyd_service import get_scrapyd_status, get_all_job_list

scrapyd = Blueprint('scrapyd', __name__)

agent = None


class CacheKeys():
    SCRAPYD_STATUS_KEY = 'scrapyd_status'
    SCRAPYD_JOB_LIST = 'scrapyd_job_list'


def fetch_scrapyd_agent(scrapyd_url):
    global agent
    agent = ScrapydAgent(scrapyd_url)


@scrapyd.route('/status/chart', methods=['GET'])
def scrapyd_status():
    if is_cacheable(current_app, CacheKeys.SCRAPYD_STATUS_KEY):
        return jsonify(get_cached(current_app, CacheKeys.SCRAPYD_STATUS_KEY))
    else:
        result = get_scrapyd_status(agent).__dict__
        set_cached(current_app, CacheKeys.SCRAPYD_STATUS_KEY, result)
        return jsonify(result)


@scrapyd.route('/job/list', methods=['GET'])
def job_list():
    if is_cacheable(current_app, CacheKeys.SCRAPYD_JOB_LIST):
        return jsonify(get_cached(current_app, CacheKeys.SCRAPYD_JOB_LIST))
    else:
        result = generate_job_list_for_jsonify()
        set_cached(current_app, CacheKeys.SCRAPYD_JOB_LIST, result)
        return jsonify(result)


def generate_job_list_for_jsonify():
    pending, running, finished = get_all_job_list(agent)
    result = {}
    result['pending'] = [p.__dict__ for p in pending]
    result['running'] = [r.__dict__ for r in running]
    result['finished'] = [f.__dict__ for f in finished]
    return result


def is_cacheable(current_app, cache_key):
    return current_app.config['ENABLE_CACHE'] and current_app.config['GLOBAL_CACHE'].get(cache_key) is not None


def set_cached(current_app, cache_key, data):
    if current_app.config['ENABLE_CACHE']:
        current_app.config['GLOBAL_CACHE'].set(cache_key, data,
                                               timeout=current_app.config['CACHE_EXPIRE'])


def get_cached(current_app, cache_key):
    return current_app.config['GLOBAL_CACHE'].get(cache_key)
