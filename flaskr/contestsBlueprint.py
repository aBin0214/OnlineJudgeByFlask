#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash

from . import MysqlUtils

bp = Blueprint('contests', __name__, url_prefix='/contests')

@bp.route("/contestSet")
@bp.route("/contestSet/<int:currentPage>")
def contestSet(currentPage=1):
    session['active'] = "Contests"
    session['currentPage_con'] = currentPage
    if session.get("contextId_con") is None:
        session["contextId_con"] = 1
    if session.get("pageSize_con") is None:
        session['pageSize_con'] = 20

    totalCount = getContestCount()
    total = totalCount//session.get("pageSize_con")
    total = total if totalCount%session.get("pageSize_con") == 0 else total+1
    session['totalPage_con'] = total

    contestSet = getContestSet(session.get('currentPage_con'),session.get('pageSize_con'))
        
    return render_template("contests/contestSet.html",contestSet=contestSet,datetime=datetime.datetime)

@bp.route("/contest/<int:contestId>/<string:next>", methods=['POST'])
@bp.route("/contest/<int:contestId>")
def contest(contestId,next='/'):
    if request.method == 'POST':
        password = request.form['contest_password']
        print(password)
        error = None
        if password is None or password == '':
            error = 'Password is required.'
        
        db = MysqlUtils.MyPyMysqlPool()
        if error is None:
            contest = db.get_one(
                'SELECT password FROM contest WHERE id_contest = {id_contest} limit 1'.format(id_contest=contestId)
            )
            if password is False:
                error = 'Incorrect contestId.'
            elif not check_password_hash(contest['password'], password):
                error = 'Incorrect password.'
        if error is not None:
            flash(error)
            return redirect(url_for(next))
    session['contestId_pro'] = contestId
    return redirect(url_for('problems.problemSet'));


def getContestSet(currentPage,pageSize):
    db = MysqlUtils.MyPyMysqlPool()
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
    finally:
        db.dispose()
    return contestSet

def getContestCount():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "SELECT count(id_contest) as cnt FROM online_judge.contest \
    where contest.id_contest != 1 limit 1;"
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get submission count failure !")
    finally:
        db.dispose()
    return res["cnt"]