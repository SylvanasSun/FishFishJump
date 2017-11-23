from flask import Blueprint, request, current_app, session, flash, redirect, url_for, render_template

user = Blueprint('user', __name__)


@user.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['ADMIN_USERNAME']:
            error = 'Invalid username.'
        elif int(request.form['password']) != current_app.config['ADMIN_PASSWORD']:
            error = 'Invalid password.'
        else:
            session['is_login'] = True
            session['username'] = request.form['username']
            flash('You were login in.')
            return redirect(url_for('home.home_page'))
    return render_template('login.html', error=error)


@user.route('/logout')
def logout():
    session.pop('is_login', None)
    session.pop('username', None)
    flash('You were login out.')
    return redirect(url_for('home.home_page'))
