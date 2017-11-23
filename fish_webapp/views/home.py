from flask import Blueprint, render_template, session

home = Blueprint('home', __name__)


@home.route('/home')
def home_page():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('home.html')
