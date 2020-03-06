#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app,jsonify
)
from werkzeug.security import check_password_hash

from . import MysqlUtils

bp = Blueprint('contests', __name__, url_prefix='/contests')

@bp.route("/contestSet")
def contestSet(currentPage=1):
    session['active'] = "Contests"
    return render_template("contests/contestSet.html")

@bp.route("/contest/<int:contestId>")
def contest(contestId):
    session['contestId_pro'] = contestId
    return redirect(url_for('problems.problemSet'));

@bp.route("/contestPermission/<int:contestId>", methods=['GET'])
def contestPermission(contestId):

    db = MysqlUtils.MyPyMysqlPool()
    contestInfo = getContestInfo(db,contestId)
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
    contestInfo = getContestInfo(db,contestId)
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
    session['currentPage_con'] = currentPage
    if session.get("contextId_con") is None:
        session["contextId_con"] = 1
    if session.get("pageSize_con") is None:
        session['pageSize_con'] = 20

    totalCount = getContestCount(db)
    total = totalCount//session.get("pageSize_con")
    total = total if totalCount%session.get("pageSize_con") == 0 else total+1
    session['totalPage_con'] = total

    contestSet = getContestSet(db,session.get('currentPage_con'),session.get('pageSize_con'))
    db.dispose()
    return render_template("contests/contestList.html",contestSet=contestSet)

def getContestSet(db,currentPage,pageSize):
    start = (currentPage-1)*pageSize
    sql = "SELECT id_contest,title,introduction,start_time,end_time,\
        is_practice,belong,is_private,password \
        FROM contest \
        where contest.id_contest != 1 \
        limit {start},{pageSize};".format(start=start,pageSize=pageSize)
    contestSet = None
    try:
        contestSet = db.get_all(sql)
    except:
        current_app.logger.error("get contest count failure !")
    return contestSet

def getContestCount(db):
    sql = "SELECT count(id_contest) as cnt FROM online_judge.contest \
    where contest.id_contest != 1 limit 1;"
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get submission count failure !")
    return res["cnt"]

def getContestInfo(db,id_contest):
    sql = "SELECT id_contest,title,introduction,start_time,end_time,is_practice,is_practice,username as belong,is_private,user.password \
        FROM contest,user \
        where contest.belong = user.id_user \
        and id_contest = {id_contest} \
        limit 1".format(id_contest=id_contest)
    contestInfo = None
    try:
        contestInfo = db.get_one(sql)
    except:
        current_app.logger.error("get contest infomation failure !")
    return contestInfo