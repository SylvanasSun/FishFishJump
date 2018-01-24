#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from fish_webapp import settings
from fish_webapp.cache import initialize_cache
from fish_webapp.cli import enable_opts
from fish_webapp.views.dashboard import dashboard
from fish_webapp.views.elasticsearch import elasticsearch, init_elasticsearch_client
from fish_webapp.views.scrapyd import scrapyd, init_scrapyd_agent
from fish_webapp.views.user import user
from flask import Flask, session, redirect, url_for, request, send_from_directory, render_template


def init_client(app):
    # initialize scrapyd agent
    init_scrapyd_agent(app.config['SCRAPYD_URL'])
    # initialize elasticsearch client
    hosts = app.config['ELASTICSEARCH_HOSTS'].split(',')
    address_list = []
    for host in hosts:
        host = host.strip()
        temp = host.split(':')
        address_list.append({
            'host': temp[0].strip(),
            'port': int(temp[1].strip())
        })
    init_elasticsearch_client(address_list)


def initialize_logging(app):
    log_file_dir = app.config.get('LOG_FILE_DIR')
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)
    log_file_name = log_file_dir + app.config.get('LOG_FILE_BASIS_NAME')
    timed_file_handler = TimedRotatingFileHandler(log_file_name, 'D', 1, 90)
    timed_file_handler.suffix = '%Y-%m-%d.log'
    root = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    if app.config.get('VERBOSE') is True or app.config.get('DEBUG') is True:
        timed_file_handler.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    root.addHandler(timed_file_handler)
    app.logger.addHandler(timed_file_handler)


app = Flask(__name__)
app.config.from_object(settings.DevelopmentConfig)
# Update configuration from command line
enable_opts(app.config)
initialize_logging(app)
app.logger.info('FishFishJump(webapp) started on %s:%s username=%s password=%s'
                % (app.config['HOST'], str(app.config['PORT']), app.config['ADMIN_USERNAME'],
                   app.config['ADMIN_PASSWORD']))

app.secret_key = os.urandom(24)

# init global cache
initialize_cache(app)

init_client(app)

# register blueprint
app.register_blueprint(dashboard, url_prefix='/supervisor/dashboard')
app.register_blueprint(user, url_prefix='/supervisor/user')
app.register_blueprint(scrapyd, url_prefix='/supervisor/scrapyd')
app.register_blueprint(elasticsearch, url_prefix='/supervisor/elasticsearch')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500), 500


@app.before_request
def login_interceptor():
    path = request.path
    if path.startswith('/supervisor'):
        if path == '/supervisor/user/login.html' or path == '/supervisor/user/login':
            return
        if not 'is_login' in session or not session['is_login']:
            return redirect(url_for('user.login'))


def main():
    app.run(host=app.config['HOST'], port=int(app.config['PORT']))


if __name__ == '__main__':
    main()
