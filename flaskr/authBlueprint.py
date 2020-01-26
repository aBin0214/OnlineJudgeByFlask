#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import MysqlUtils
from . import FormUtils


bp = Blueprint('auth', __name__, url_prefix='/auth')


# bp.route 关联了 URL /register 和 register 视图函数。
# 当 Flask 收到一个指向 /auth/register 的请求时就会调用 register 视图并把其返回值作为响应。
@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    注册
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if username is None or username == '':
            flash('The username cannot be empty !')
        elif password is None or password == '':
            flash('The password cannot be empty !')
        elif confirm_password is None or confirm_password == '':
            flash('The two passwords you entered did not match !')
        else:
            db = MysqlUtils.MyPyMysqlPool()
            error = None
            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif db.get_one('SELECT id_user FROM user WHERE username = \'{}\' limit 1;'.format(username)) is not False:
                error = 'User {} is already registered.'.format(username)
            elif password != confirm_password:
                error = 'The passwords must be the same'

            if error is None:
                sql = 'INSERT INTO user (username, password, is_admin) VALUES (\'{}\',\'{}\',\'{}\')'\
                    .format(username, generate_password_hash(password), 0)
                db.insert(sql)
                db.dispose()
                return redirect(url_for('auth.login'))
            flash(error)
            db.dispose()
    user = FormUtils.UserFrom()
    return render_template('auth/register.html',user=user)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    登录
    :return:
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username is None or username == '':
            flash('The username cannot be empty !')
        elif password is None or password == '':
            flash('The password cannot be empty !')
        else:
            db = MysqlUtils.MyPyMysqlPool()
            error = None
            user = db.get_one(
                'SELECT id_user,username,password,is_admin FROM user WHERE username = \'{}\' limit 1'.format(username)
            )

            if user is False:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['id_user'] = user['id_user']
                session["username"] = user['username']
                session['password'] = user['password']
                db.dispose()
                return redirect(url_for('index'))
            flash(error)
            db.dispose()
    user = FormUtils.UserFrom()
    return render_template('auth/login.html',user = user)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/logout')
def logout():
    """
    登出
    :return:
    """
    session.clear()
    return redirect(url_for('index'))

