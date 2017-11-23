import settings
import os
from flask import Flask, session, redirect, url_for, request
from views.home import home
from views.user import user

app = Flask(__name__)
app.config.from_object(settings.DevelopmentConfig)
app.secret_key = os.urandom(24)
app.register_blueprint(home)
app.register_blueprint(user)


@app.before_request
def login_interceptor():
    if request.path == '/login.html' or request.path == '/login':
        return
    if not 'is_login' in session or not session['is_login']:
        return redirect(url_for('user.login'))


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'])
