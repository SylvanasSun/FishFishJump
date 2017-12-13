import os

import settings
from flask import Flask, session, redirect, url_for, request, send_from_directory, render_template
from views.dashboard import dashboard
from views.scrapyd import scrapyd, fetch_scrapyd_agent
from views.user import user

app = Flask(__name__)
app.config.from_object(settings.DevelopmentConfig)
app.secret_key = os.urandom(24)

# init global cache
if app.config['ENABLE_CACHE']:
    from werkzeug.contrib.cache import SimpleCache

    app.config['GLOBAL_CACHE'] = SimpleCache()

# register scrapyd agent
fetch_scrapyd_agent(app.config['SCRAPYD_URL'])

app.register_blueprint(dashboard, url_prefix='/supervisor/dashboard')
app.register_blueprint(user, url_prefix='/supervisor/user')
app.register_blueprint(scrapyd, url_prefix='/supervisor/scrapyd')


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


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
