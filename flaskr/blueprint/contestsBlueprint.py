#!/usr/bin/env python
# -*- coding:utf-8 -*-

import functools
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app,jsonify
)
from werkzeug.security import check_password_hash

from flaskr.utils import MysqlUtils
from flaskr.utils import PagingUtils

from flaskr.server import ContestServer

bp = Blueprint('contests', __name__, url_prefix='/contests')

@bp.route("/contestSet")
def contestSet(currentPage=1):
    session['active'] = "Contests"
    return render_template("contests/contestSet.html")

@bp.route("/contest/<int:contestId>")
def contest(contestId):
    session['contestId'] = contestId
    return redirect(url_for('contestDetail.problemSet'));

@bp.route("/contestPermission/<int:contestId>", methods=['GET'])
def contestPermission(contestId):

    db = MysqlUtils.MyPyMysqlPool()
    contestInfo = ContestServer.getContestInfo(db,contestId)
    db.dispose()
    error = None
    if session.get('id_user') is None or session.get('id_user') == '':
        error = "Please log in first!"
        flash(error,"info")
    if contestInfo['start_time'] > datetime.datetime.now():
        error = "The contest hasn't started yet!"
        flash(error,"info")
    if error is None:
        if contestInfo["is_private"]:
            return jsonify({
                "result":"success",
                "is_private":1,
                "title":contestInfo["title"],
                "nextUrl":url_for("contests.judgeContestPass")
            })
        else:
            return jsonify({
                "result":"success",
                "is_private":0,
                "nextUrl":url_for("contests.contest",contestId=contestId)
            })
    return jsonify({
        "result":"failure",
        "describe":error
    })

@bp.route("/judgeContestPass", methods=['POST'])
def judgeContestPass():
    contestId = request.form["contestId"]
    password = request.form["password"]
    db = MysqlUtils.MyPyMysqlPool()
    contestInfo = ContestServer.getContestInfo(db,contestId)
    db.dispose()
    error = None
    if password is None or password == '':
        error = "Password is required."
        flash(error,'danger')

    if error is None and check_password_hash(contestInfo['password'], password) is False:
        error = 'Incorrect password.'
        flash(error,"danger")
    
    if error is None:
        return jsonify({
            "result":"success",
            "nextUrl":url_for("contests.contest",contestId=contestId)
        })
    return jsonify({
        "result":"failure"
    })

@bp.route("/showContestList")
@bp.route("/showContestList/<int:currentPage>",methods=["POST","GET"])
def showContestList(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    PagingUtils.Paging(currentPage,ContestServer.getContestCount(db))
    # contestSet = getContestSet(db,session.get('currentPage'),session.get('pageSize'))
    contestSet = ContestServer.getContestList(db,session.get('currentPage'),session.get('pageSize'))
    db.dispose()
    return render_template("contests/contestList.html",contestSet=contestSet)