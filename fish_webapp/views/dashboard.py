from flask import Blueprint, render_template, session, url_for
from utils.http_utils import request, RETURN_JSON

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def home_page():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('home.html')


@dashboard.route('/job/list')
def job_list_page():
    return render_template('job_list.html')


@dashboard.route('/project/list')
def project_list_page():
    return render_template('project_list.html')


@dashboard.route('/spider/list')
def spider_list_page():
    return render_template('spider_list.html')


@dashboard.route('/job/schedule')
def schedule_page():
    return render_template('schedule.html')
