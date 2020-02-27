#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,jsonify
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash

from . import MysqlUtils

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/login",methods=["POST","GET"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if username is None or username == '':
            error = 'Username is required.'
        elif error is None and (password is None or password == ''):
            error = 'Password is required.'
        
        db = MysqlUtils.MyPyMysqlPool()
        if error is None:
            user = db.get_one(
                'SELECT id_user,username,password,is_admin FROM user WHERE username = \'{}\' limit 1'.format(username)
            )
            print(user)
            if user is False:
                error = 'Incorrect username.'
            if user['is_admin'] == 0:
                error = "This is not an administrator account."
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

        if error is None:
            session['id_user_admin'] = user['id_user']
            session["username_admin"] = user['username']
            session['password_admin'] = user['password']
            db.dispose()
            flash('Admin Login successfully!','success')
            return jsonify({
                "result":"success"
            })
        flash(error,'danger')
        db.dispose()
        return jsonify({
            "result":"failure",
            "describe":error
        })
    else:
        return render_template("admin/adminLogin.html")

@bp.route("/index")
def index():
    judgeAdmin()
    return render_template("admin/adminBase.html")

def judgeAdmin():
    if session.get('id_user_admin') is None:
        flash("Please log in first.",'info')
        return redirect(url_for('admin.login'))