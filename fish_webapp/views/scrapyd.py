from fish_webapp.cache import CacheKeys, is_cacheable, get_cached, set_cached
from fish_webapp.scrapyd.scrapyd_agent import ScrapydAgent
from fish_webapp.scrapyd.scrapyd_service import get_scrapyd_status, get_all_job_list, packing_job_ext_info, \
    get_logs_info, \
    cancel_job, add_version, get_all_project_list, get_all_spider_list, schedule_job
from flask import Blueprint, jsonify, current_app, request

scrapyd = Blueprint('scrapyd', __name__)

agent = None


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


@scrapyd.route('/job/logs', methods=['GET'])
def logs_info():
    if is_cacheable(current_app, CacheKeys.SCRAPYD_LOGS_INFO):
        return jsonify(get_cached(current_app, CacheKeys.SCRAPYD_LOGS_INFO))
    else:
        result = get_logs_info(agent, request.args.get('project_name'), request.args.get('spider_name'))
        set_cached(current_app, CacheKeys.SCRAPYD_LOGS_INFO, result)
        return jsonify(result)


@scrapyd.route('/job/cancel', methods=['POST'])
def cancel_job():
    cancel_job(agent, request.form['project_name'], request.form['job_id'])


@scrapyd.route('/project/add/version', methods=['POST'])
def add_version():
    add_version(agent, request.form['project_name'], request.form['version_name'], request.files['project_egg'])


@scrapyd.route('/project/list', methods=['GET'])
def project_list():
    if is_cacheable(current_app, CacheKeys.SCRAPYD_PROJECT_LIST):
        return jsonify(get_cached(current_app, CacheKeys.SCRAPYD_PROJECT_LIST))
    else:
        result = get_all_project_list(agent)
        result = [r.__dict__ for r in result]
        set_cached(current_app, CacheKeys.SCRAPYD_PROJECT_LIST, result)
        return jsonify(result)


@scrapyd.route('/spider/list', methods=['GET'])
def spider_list():
    if is_cacheable(current_app, CacheKeys.SCRAPYD_SPIDER_LIST):
        return jsonify(get_cached(current_app, CacheKeys.SCRAPYD_SPIDER_LIST))
    else:
        result = get_all_spider_list(agent)
        result = [r.__dict__ for r in result]
        set_cached(current_app, CacheKeys.SCRAPYD_SPIDER_LIST, result)
        return jsonify(result)


@scrapyd.route('/job/schedule', methods=['POST'])
def schedule():
    schedule_job(agent,
                 request.form['project_name'],
                 request.form['spider_name'],
                 int(request.form['priority']),
                 request.form['setting'],
                 request.form['job_id'],
                 request.form['project_version'],
                 request.form['args']
                 )


def generate_job_list_for_jsonify():
    pending, running, finished = get_all_job_list(agent)
    result = {}
    result['pending'] = [packing_job_ext_info(p).__dict__ for p in pending]
    result['running'] = [packing_job_ext_info(r).__dict__ for r in running]
    result['finished'] = [packing_job_ext_info(f).__dict__ for f in finished]
    return result
