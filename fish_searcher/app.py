#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from flask import Flask, send_from_directory, render_template

from fish_searcher import settings
from fish_searcher.cli import enable_opts
from fish_searcher.views.search import search_view, init_elasticsearch, init_redis, init_cache, init_thread_pool


def initialize_logging(app):
    log_file_dir = app.config.get('LOG_FILE_DIR')
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)
    log_file_path = log_file_dir + app.config.get('LOG_FILE_BASIS_NAME')
    file_handler = logging.FileHandler(log_file_path)
    root = logging.getLogger()
    logging.basicConfig(level=logging.INFO)
    if app.config.get('VERBOSE') or app.config.get('DEBUG'):
        root.setLevel(logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    app.logger.addHandler(file_handler)


app = Flask(__name__)
app.config.from_object(settings.DevelopmentConfig)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def error_404(e):
    return render_template('error.html', error_code=404), 404


@app.errorhandler(500)
def error_500(e):
    return render_template('error.html', error_code=500), 500


def main():
    enable_opts(app.config)
    es_index = app.config['ELASTICSEARCH_INDEX']
    es_doc_type = app.config['ELASTICSEARCH_DOC_TYPE']
    if isinstance(es_index, str):
        app.config['ELASTICSEARCH_INDEX'] = es_index.split(',')
    if isinstance(es_doc_type, str):
        app.config['ELASTICSEARCH_DOC_TYPE'] = es_doc_type.split(',')
    initialize_logging(app)
    init_elasticsearch(app)
    init_redis(app)
    init_cache()
    init_thread_pool()
    # register blueprint
    app.register_blueprint(search_view)
    # start run
    app.run(host=app.config['HOST'], port=int(app.config['PORT']))


if __name__ == '__main__':
    main()
