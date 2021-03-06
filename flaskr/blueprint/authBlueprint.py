#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.utils import MysqlUtils
from flaskr.server import UserServer


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    注册
    """
    session['active'] = "Register"
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    db = MysqlUtils.MyPyMysqlPool()
    error = None
    if username is None or username == '':
        error = 'Username is required.'
    elif password is None or password == '':
        error = 'Password is required.'
    elif confirm_password is None or confirm_password == '':
        error = 'The two passwords you entered did not match !'
    elif UserServer.getUser(db, username=username) != {}:
        error = 'User {} is already registered.'.format(username)
    elif password != confirm_password:
        error = 'The passwords must be the same'

    if error is None:
        if UserServer.userRegister(db, username, generate_password_hash(password)):
            db.dispose()
            flash('Registered successfully!','success')
            return jsonify({
                "result":"success"
            })
        else:
            error = "Insert user into mysql-database failure"
            current_app.logger.error(error)
    flash(error,'danger')
    db.dispose()
    return jsonify({
        "result":"failure",
        "describe":error
    })


@bp.route('/login', methods=['POST'])
def login():
    """
    登录
    """
    session['active'] = "Login"
    username = request.form['username']
    password = request.form['password']
    error = None
    if username is None or username == '':
        error = 'Username is required.'
    elif error is None and (password is None or password == ''):
        error = 'Password is required.'
    
    db = MysqlUtils.MyPyMysqlPool()
    if error is None:
        user = UserServer.getUser(db, username=username)
        if user is False:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

    if error is None:
        session['id_user'] = user['id_user']
        session["username"] = user['username']
        session['password'] = user['password']
        session["is_admin"] = True if user["is_admin"] == 1 else False
        db.dispose()
        flash('Login successfully!','success')
        return jsonify({
            "result":"success"
        })
    flash(error,'danger')
    db.dispose()
    return jsonify({
        "result":"failure",
        "describe":error
    })

@bp.route("/showLogin")
def showLogin():
    return render_template('auth/login.html') 

@bp.route("/showRegister")
def showRegister():
    return render_template('auth/register.html') 

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
    """
    session['id_user'] = None
    session["username"] = None
    session['password'] = None
    session["is_admin"] = None
    flash("Log Out Success.","success")
    return jsonify({
        "result":"success"
    })

