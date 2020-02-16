#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,jsonify,current_app
)
from werkzeug.exceptions import abort
import datetime

from . import MysqlUtils

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/userIndex/<int:userId>")
def userIndex(userId):
    g.userId = userId
    session['active'] = "User"
    return render_template("user/userIndex.html")

@bp.route("/profile",methods=['POST'])
def profile():
    userId = request.form.get("userId")
    proCnt = {
        "24hours":0,
        "7days":0,
        "30days":0,
        "OverallSolved":0,
        "OverallAttempted":0
    }
    proCnt["24hours"] = getProCount(userId,1,11)
    proCnt["7days"] = getProCount(userId,7,11)
    proCnt["30days"] = getProCount(userId,30,11)
    proCnt["OverallSolved"] = getProCount(userId,-1,11)
    proCnt["OverallAttempted"] = getProCount(userId,-1,-1)
    return render_template("user/profile.html",proCnt=proCnt)

@bp.route("/detail",methods=['POST'])
def detail():
    userId = request.form.get("userId")
    solvedList = getProList(userId)
    failedList = getProList(userId,False)
    if solvedList is False or solvedList is None:
        solvedList = {}
    if failedList is False or failedList is None:
        failedList = {}
    return render_template("user/detail.html",solvedList=solvedList,failedList=failedList)

@bp.route("/report",methods=['POST'])
def report():
    userId = request.form.get("userId")
    return render_template("user/report.html")

@bp.route("/showUpdate")
def showUpdate():
    return render_template("user/updateUser.html")

def getProCount(userId,interval=-1,state=-1):
    stateStr = ""
    if state != -1:
        stateStr = "and s.state = {}".format(state)
    intervalStr = ""
    if interval != -1:
        intervalStr = "and s.submit_time > '{}'".format(
            (datetime.datetime.now()+datetime.timedelta(days=interval)).strftime("%Y-%m-%d %H:%M:%S")
        )

    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(DISTINCT cp.id_problem) as cnt \
            from solution as s,contest_problem as cp \
            where s.id_contest_problem = cp.id_contest_problem \
            and id_user = {id_user} \
            {state}\
            {time}\
            limit 1".format(id_user=userId,state=stateStr,time=intervalStr)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user count failure !")
    finally:
        db.dispose()
    if res is False or res is None:
        return 0
    return res['cnt']

def getProList(userId,isSolved=True):
    db = MysqlUtils.MyPyMysqlPool()
    sql = ""
    if isSolved:
        sql = "select distinct cp.id_problem,cp.id_contest_problem\
            from solution as s,contest_problem as cp\
            where s.id_contest_problem = cp.id_contest_problem\
            and s.id_user = {id_user}\
            and s.state = 11\
            order by s.submit_time".format(id_user=userId)
    else:
        sql = "select distinct cp.id_problem,cp.id_contest_problem\
            from online_judge.solution as s,online_judge.contest_problem as cp\
            where s.id_contest_problem = cp.id_contest_problem\
            and id_user = {id_user}\
            and cp.id_problem not in (select distinct cp.id_problem\
            from online_judge.solution as s,online_judge.contest_problem as cp\
            where s.id_contest_problem = cp.id_contest_problem\
            and id_user = {id_user}\
            and s.state = 11)\
            order by s.submit_time".format(id_user=userId)
        pass
    solvedPro = None
    try:
        solvedPro = db.get_all(sql)
    except:
        current_app.logger.error("get user:{} {} problem failure !".format(userId,"solved" if isSolved else "unsolved"))
    finally:
        db.dispose()
    return solvedPro