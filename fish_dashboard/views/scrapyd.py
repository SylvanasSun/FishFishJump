#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, current_app, request

from fish_dashboard.cache import CacheKeys
from fish_dashboard.fault import fault_tolerant_by_backup
from fish_dashboard.scrapyd.scrapyd_agent import ScrapydAgent
from fish_dashboard.scrapyd.scrapyd_service import get_scrapyd_status, get_all_job_list, packing_job_ext_info, \
    get_logs_info, cancel_job, add_version, get_all_project_list, get_all_spider_list, schedule_job

scrapyd = Blueprint('scrapyd', __name__)

agent = None


def init_scrapyd_agent(scrapyd_url):
    global agent
    agent = ScrapydAgent(scrapyd_url)


@scrapyd.route('/status/chart', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.SCRAPYD_STATUS_KEY,
                          serializable_func=jsonify)
def scrapyd_status():
    return get_scrapyd_status(agent).__dict__


@scrapyd.route('/job/list', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.SCRAPYD_JOB_LIST,
                          serializable_func=jsonify)
def job_list():
    return generate_job_list_for_jsonify()


@scrapyd.route('/job/logs', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.SCRAPYD_LOGS_INFO,
                          serializable_func=jsonify)
def logs_info():
    return get_logs_info(agent, request.args.get('project_name'), request.args.get('spider_name'))


@scrapyd.route('/job/cancel', methods=['POST'])
def cancel_job():
    cancel_job(agent, request.form['project_name'], request.form['job_id'])


@scrapyd.route('/project/add/version', methods=['POST'])
def add_version():
    add_version(agent, request.form['project_name'], request.form['version_name'], request.files['project_egg'])


@scrapyd.route('/project/list', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.SCRAPYD_PROJECT_LIST,
                          serializable_func=jsonify)
def project_list():
    result = get_all_project_list(agent)
    result = [r.__dict__ for r in result]
    return result


@scrapyd.route('/spider/list', methods=['GET'])
@fault_tolerant_by_backup(flask_app=current_app,
                          key=CacheKeys.SCRAPYD_SPIDER_LIST,
                          serializable_func=jsonify)
def spider_list():
    result = get_all_spider_list(agent)
    result = [r.__dict__ for r in result]
    return result


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
