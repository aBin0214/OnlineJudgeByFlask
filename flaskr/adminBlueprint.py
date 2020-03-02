#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,jsonify,current_app,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash
import os

from . import MysqlUtils
from . import LogUtils
from . import CodeHighlightUtils
from . import problemUtils

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

@bp.route("/showLogs",methods=["POST","GET"])
@bp.route("/showLogs/<int:currentPage>",methods=["POST","GET"])
def showLogs(currentPage=1):
    if request.method == "POST":
        tag = request.form.get("tag")
        session["logs_tag"] = tag
    else:
        tag = session.get("logs_tag")
    session["currentPage_logs"] = currentPage
    if session.get("pageSize_logs") is None:
        session["pageSize_logs"] = 20
    logList = LogUtils.getLogListByTag(tag)

    if not logList:
        session['totalPage_logs'] = 0
    else:
        totalCount = logList[-1]["id_log"]
        total = totalCount//session.get("pageSize_logs")
        total = total if totalCount%session.get("pageSize_logs") == 0 else total+1
        session['totalPage_logs'] = total

    logList = logList[(currentPage-1)*session.get("pageSize_logs"):currentPage*session.get("pageSize_logs")]
    return render_template("admin/logList.html",logList=logList)

@bp.route("/users",methods=["POST","GET"])
@bp.route("/users/<int:currentPage>",methods=["POST","GET"])
def users(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()

    session['currentPage_users'] = currentPage
    if session.get("pageSize_users") is None:
        session['pageSize_users'] = 20

    totalCount = getUserCount(db)
    total = totalCount//session.get("pageSize_users")
    total = total if totalCount%session.get("pageSize_users") == 0 else total+1
    session['totalPage_users'] = total

    userList = getUserList(db,session.get('currentPage_users'),session.get('pageSize_users'))

    db.dispose()
    return render_template("admin/users.html",userList=userList)

@bp.route("/problems",methods=["POST","GET"])
@bp.route("/problems/<int:currentPage>",methods=["POST","GET"])
def problems(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()

    session['currentPage_problems'] = currentPage
    if session.get("pageSize_problems") is None:
        session['pageSize_problems'] = 20

    totalCount = getProblemCount(db)
    total = totalCount//session.get("pageSize_problems")
    total = total if totalCount%session.get("pageSize_problems") == 0 else total+1
    session['totalPage_problems'] = total

    problemList = getProblemList(db,session.get('currentPage_problems'),session.get('pageSize_problems'))
    db.dispose()
    return render_template("admin/problems.html",problemList=problemList)

@bp.route("/logDetail",methods=["POST"])
def logDetail():
    path = request.form.get("path")
    logContent = LogUtils.readLog(path)
    logContent["filename"] = os.path.split(path)[1]
    logContent["content"] = CodeHighlightUtils.CodeHighlight.codeTranslate(logContent["content"],'python')
    return render_template("admin/logDetail.html",logContent=logContent)

@bp.route("/exportLog",methods=["POST"])
def exportLog():
    filePath = request.form.get("filePath")
    dirname,filename = os.path.split(filePath)[0],os.path.split(filePath)[1]
    if os.path.isfile(filePath):
        return send_from_directory(dirname,filename,as_attachment=True)

@bp.route("/createProblem",methods=["POST","GET"])
def createProblem():
    if request.method == "GET":
        return render_template("admin/createProblem.html")
    problemTitle = request.form.get("problemTitle")
    timeLimit = request.form.get("timeLimit")
    memoryLimit = request.form.get("memoryLimit")
    describe = request.form.get("describe")
    error = None
    if problemTitle == "" or problemTitle == None:
        error = "problemTitle is empty."
    elif timeLimit == "" or timeLimit == None:
        error = "timeLimit is empty."
    elif memoryLimit == "" or memoryLimit == None:
        error = "memoryLimit is empty."
    elif describe == "" or describe == None:
        error = "describe is empty."

    userId = session.get("id_user")
    
    if error is None:
        db = MysqlUtils.MyPyMysqlPool()
        try:
            sql = 'INSERT INTO problem (title,create_by, time_limit, mem_limit) VALUES (\'{}\',\'{}\',\'{}\',\'{}\')'\
                .format(problemTitle, userId,timeLimit, memoryLimit)
            db.insert(sql)
            problemId = db.get_one("select max(id_problem) as id from problem limit 1;")["id"]
            problemUtils.saveProblemDescribe(problemId,describe)
            flash('Created problem successfully!','success')
        except:
            error = "Created problem failure."
            current_app.logger.error(error)
        finally:
            db.dispose()
    if error is None:
        return jsonify({
            "result":"success"
        })
    flash(error,'danger')
    return jsonify({
        "result":"failure"
    })

@bp.route("/contests",methods=["POST","GET"])
@bp.route("/contests/<int:currentPage>",methods=["POST","GET"])
def contests(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()

    session['currentPage_contests'] = currentPage
    if session.get("pageSize_contests") is None:
        session['pageSize_contests'] = 20

    totalCount = getContestCount(db)
    total = totalCount//session.get("pageSize_contests")
    total = total if totalCount%session.get("pageSize_contests") == 0 else total+1
    session['totalPage_contests'] = total
    contestList = getContestList(db,session.get('currentPage_contests'),session.get('pageSize_contests'))

    db.dispose()
    return render_template("admin/contests.html",contestList=contestList)

def getUserCount(db):
    sql = "select count(id_user) as cnt from user;"
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user count failure !")
    if res is False or res is None:
        return 0
    return res["cnt"]

def getProblemCount(db):
    sql = "select count(id_problem) as cnt from problem;"
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user count failure !")
    if res is False or res is None:
        return 0
    return res["cnt"]

def getContestCount(db):
    sql = "select count(id_contest) as cnt from contest;"
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user count failure !")
    if res is False or res is None:
        return 0
    return res["cnt"]

def getUserList(db,currentPage,pageSize):
    start = (currentPage-1) * pageSize
    sql = "select id_user,username,password from user limit {start},{pageSize}".format(start=start,pageSize=pageSize)
    userList = None
    try:
        userList = db.get_all(sql)
    except:
        current_app.logger.error("get user list failure !")
    if userList is False or userList is None:
        return []
    return userList

def getProblemList(db,currentPage,pageSize):
    start = (currentPage-1) * pageSize
    sql = "SELECT id_problem,title,username,is_publish \
        FROM problem,user \
        where problem.create_by = user.id_user limit {start},{pageSize};".format(start=start,pageSize=pageSize)
    problemList = None
    try:
        problemList = db.get_all(sql)
    except:
        current_app.logger.error("get problem list failure !")
    if problemList is False or problemList is None:
        return []
    return problemList

def getContestList(db,currentPage,pageSize):
    start = (currentPage-1) * pageSize
    sql = "SELECT id_contest,title,introduction,start_time,end_time,\
    is_practice,belong,is_private,password FROM contest limit {start},{pageSize};".format(start=start,pageSize=pageSize)
    contestList = None
    try:
        contestList = db.get_all(sql)
    except:
        current_app.logger.error("get contest list failure !")
    if contestList is False or contestList is None:
        return []
    return contestList



def judgeAdmin():
    if session.get('is_admin') is None:
        flash("Please log in first.",'info')
        return redirect(url_for('admin.login'))