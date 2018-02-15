#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, current_app, session, redirect, url_for, render_template

from fish_core.utils.common_utils import check_validity_for_dict
from fish_dashboard.fault import register_alarm_email

user = Blueprint('user', __name__)


@user.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['ADMIN_USERNAME']:
            error = 'Invalid username.'
        elif request.form['password'] != current_app.config['ADMIN_PASSWORD']:
            error = 'Invalid password.'
        else:
            session['is_login'] = True
            session['username'] = request.form['username']
            _handle_email_info(request)
            return redirect(url_for('dashboard.home_page'))
    return render_template('login.html', error=error)


@user.route('/logout')
def logout():
    session.pop('is_login', None)
    session.pop('username', None)
    return redirect(url_for('dashboard.home_page'))


def _handle_email_info(request):
    keys = ['email_server_host', 'email_server_port', 'sender_addr', 'receiver_name', 'receiver_addr',
            'email_server_authorization_code']
    if check_validity_for_dict(keys, request.form):
        register_alarm_email(host=request.form['email_server_host'],
                             port=int(request.form['email_server_port']),
                             sender_addr=request.form['sender_addr'],
                             receiver=request.form['receiver_name'],
                             receiver_addr=request.form['receiver_addr'],
                             authorization_code=request.form['email_server_authorization_code'],
                             flask_app=current_app)
