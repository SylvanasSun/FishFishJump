from flask import Blueprint, render_template, session

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def home_page():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('home.html')


@dashboard.route('/scrapy/job/list')
def scrapy_job_list_page():
    return render_template('scrapy/job_list.html')


@dashboard.route('/scrapy/project/list')
def scrapy_project_list_page():
    return render_template('scrapy/project_list.html')


@dashboard.route('/scrapy/spider/list')
def scrapy_spider_list_page():
    return render_template('scrapy/spider_list.html')


@dashboard.route('/scrapy/job/schedule')
def scrapy_schedule_page():
    return render_template('scrapy/schedule.html')


@dashboard.route('/elasticsearch/cluster/health')
def elasticsearch_cluster_health():
    return render_template('elasticsearch/cluster_health.html')


@dashboard.route('/elasticsearch/cluster/indices/health')
def elasticsearch_cluster_indices_health():
    return render_template('elasticsearch/indices_health.html')


@dashboard.route('/elasticsearch/cluster/stats')
def elasticsearch_cluster_stats():
    return render_template('elasticsearch/cluster_stats.html')


@dashboard.route('/elasticsearch/nodes/info')
def elasticsearch_nodes_info():
    return render_template('elasticsearch/nodes_info.html')
