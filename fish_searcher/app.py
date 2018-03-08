#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os

from flask import Flask, send_from_directory, render_template, request
from flask_socketio import SocketIO, emit

from fish_searcher import settings
from fish_searcher.cli import enable_opts
from fish_searcher.views.search import search_view, init_elasticsearch, init_redis, init_cache, init_thread_pool, \
    query_from_es, packing_page_items


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
# enable websockets
socketio = SocketIO()


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


@socketio.on('suggest_result', namespace='/suggest')
def on_suggest_result(keyword):
    keyword = keyword['data']
    result = query_from_es(size=5, from_=0, keywords=keyword)
    pages_info = packing_page_items(result['hits']['hits'], 0, 3)[0]
    emit('render_suggest_list', {'data': json.dumps(pages_info, ensure_ascii=False)})


@socketio.on('disconnect', namespace='/suggest')
def on_suggest_disconnect():
    app.logger.debug('Client %s already disconnect' % request.remote_addr)


@socketio.on('connect', namespace='/suggest')
def on_suggest_connect():
    app.logger.debug('Client %s already connect' % request.remote_addr)


def main():
    enable_opts(app.config)
    es_index = app.config['ELASTICSEARCH_INDEX']
    es_doc_type = app.config['ELASTICSEARCH_DOC_TYPE']
    if isinstance(es_index, str):
        app.config['ELASTICSEARCH_INDEX'] = es_index.split(',')
    if isinstance(es_doc_type, str):
        app.config['ELASTICSEARCH_DOC_TYPE'] = es_doc_type.split(',')
    app.config['SECRET_KEY'] = 'a mysterious fish'
    # register blueprint
    initialize_logging(app)
    init_elasticsearch(app)
    init_redis(app)
    init_cache()
    init_thread_pool()
    app.register_blueprint(search_view)
    # run
    socketio.init_app(app)
    socketio.run(app, host=app.config['HOST'], port=int(app.config['PORT']))


if __name__ == '__main__':
    main()
