#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,jsonify,current_app
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
            session['id_user'] = user['id_user']
            session["username"] = user['username']
            session['password'] = user['password']
            session["is_admin"] = True
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
        if session.get('is_admin') is not None:
            return redirect(url_for('admin.index'))
        return render_template("admin/adminLogin.html")

@bp.route("/index")
def index():
    judgeAdmin()
    return render_template("admin/adminBase.html")

@bp.route("/dashBoard",methods=["POST"])
def dashBoard():
    return render_template("admin/dashBoard.html")

@bp.route("/management",methods=["POST"])
def management():
    return render_template("admin/management.html")

@bp.route("/logs",methods=["POST"])
def logs():
    return render_template("admin/logs.html")

@bp.route("/users",methods=["POST"])
def users():
    db = MysqlUtils.MyPyMysqlPool()
    userList = getUserList(db)
    db.dispose()
    return render_template("admin/users.html",userList=userList)

@bp.route("/problems",methods=["POST"])
def problems():
    return render_template("admin/problems.html")

@bp.route("/contests",methods=["POST"])
def contests():
    return render_template("admin/contests.html")

def getUserList(db):
    sql = "select id_user,username,password from user"
    userList = None
    try:
        userList = db.get_all(sql)
    except:
        current_app.logger.error("get user list failure !")
    if userList is False or userList is None:
        return []
    return userList

def judgeAdmin():
    if session.get('is_admin') is None:
        flash("Please log in first.",'info')
        return redirect(url_for('admin.login'))