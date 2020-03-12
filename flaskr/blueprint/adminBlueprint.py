#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,jsonify,current_app,send_from_directory
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash
import os
import datetime

from flaskr.utils import MysqlUtils
from flaskr.utils import LogUtils
from flaskr.utils import CodeHighlightUtils
from flaskr.utils import ProblemUtils
from flaskr.utils import PagingUtils

from flaskr.server import UserServer
from flaskr.server import ProblemServer
from flaskr.server import ContestServer

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
            user = UserServer.getUser(db, username=username)
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
    if not judgeAdmin():
        return redirect(url_for('admin.login'))
    return render_template("admin/adminBase.html")

@bp.route("/dashBoard",methods=["POST"])
def dashBoard():
    if not judgeAdmin():
        return redirect(url_for('admin.login'))
    return render_template("admin/dashBoard.html")

@bp.route("/management",methods=["POST"])
def management():
    if not judgeAdmin():
        return redirect(url_for('admin.login'))
    return render_template("admin/management.html")

@bp.route("/logs",methods=["POST"])
def logs():
    if not judgeAdmin():
        return redirect(url_for('admin.login'))
    return render_template("admin/logs.html")

@bp.route("/showLogs",methods=["POST","GET"])
@bp.route("/showLogs/<int:currentPage>",methods=["POST","GET"])
def showLogs(currentPage=1):
    if request.method == "POST":
        tag = request.form.get("tag")
        session["logs_tag"] = tag
    else:
        tag = session.get("logs_tag")
    logList = LogUtils.getLogListByTag(tag)

    if not logList:
        totalCount = 0
    else:
        totalCount = logList[-1]["id_log"]
    PagingUtils.Paging(currentPage,totalCount)

    logList = logList[(currentPage-1)*session.get("pageSize"):currentPage*session.get("pageSize")]
    return render_template("admin/logList.html",logList=logList)

@bp.route("/users",methods=["POST","GET"])
@bp.route("/users/<int:currentPage>",methods=["POST","GET"])
def users(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()

    PagingUtils.Paging(currentPage, UserServer.getUserCount(db))
    userList = UserServer.getUserList(db, session.get('currentPage'), session.get('pageSize'))

    db.dispose()
    return render_template("admin/users.html",userList=userList)

@bp.route("/problems",methods=["POST","GET"])
@bp.route("/problems/<int:currentPage>",methods=["POST","GET"])
def problems(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()

    PagingUtils.Paging(currentPage, ProblemServer.getProblemCount(db))

    problemList = ProblemServer.getProblemList(db, session.get('currentPage'), session.get('pageSize'))
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

@bp.route("/createProblem",methods=["POST"])
def createProblem():
    proContent = {}
    proContent["id_problem"] = -1
    proContent["webTitle"] = "Created Problem"
    proContent["title"] = ""
    proContent["time_limit"] = 1000
    proContent["mem_limit"] = 65535
    proContent["describe"] = "Enter the description of the problem here\n\n" \
        "### Input\nEnter the description of the input here\n" \
        "### Output\nEnter the description of the output here\n" \
        "### Sample Input\n```\nEnter the sample Input here\n```\n" \
        "### Sample Output\n```\nEnter the sample output here\n```\n" \
        "### Hint\nEnter the hint of the problem here\n"
    return render_template("admin/editProblem.html",proContent=proContent)

@bp.route("/updateProblem",methods=["POST"])
def updateProblem():
    db = MysqlUtils.MyPyMysqlPool()
    problemId = request.form.get("id_problem")
    proContent = ProblemServer.getProblemById(db, problemId)
    proContent["webTitle"] = "Update Problem"
    proContent["describe"] = ProblemUtils.readProblemDescribe(problemId)["content"]
    db.dispose
    return render_template("admin/editProblem.html",proContent=proContent)

@bp.route("/saveProblem",methods=["POST"])
def saveProblem():
    problemId = request.form.get("id_problem")
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
    # print("problemId:{}".format(problemId))
    # print(type(problemId))
    isUpdate = False if problemId == "-1" or problemId == None else True
    if error is None:
        db = MysqlUtils.MyPyMysqlPool()
        problem = {}
        problem["title"] = problemTitle
        problem["create_by"] = userId
        problem["time_limit"] = timeLimit
        problem["mem_limit"] = memoryLimit
        problem["id_problem"] = problemId
        isSuccess = False
        if isUpdate:
            isSuccess = ProblemServer.updateProblem(db, problem)
        else:
            isSuccess = ProblemServer.insertProblem(db, problem)
        if isSuccess:
            ProblemUtils.saveProblemDescribe(problemId,describe)
            flash('{} problem successfully!'.format("Created" if isUpdate is False else "Update"),'success')
        else:
            error = "{} problem failure.".format("Created" if isUpdate is False else "Update")
            current_app.logger.error(error)
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
    PagingUtils.Paging(currentPage, ContestServer.getContestCount(db))
    contestList = ContestServer.getContestList(db, session.get('currentPage'), session.get('pageSize'))
    db.dispose()
    return render_template("admin/contests.html",contestList=contestList)

@bp.route("/createContest",methods=["POST"])
def createContest():
    contestContent = {}
    contestContent["id_contest"] = -1
    contestContent["webTitle"] = "Created Contest"
    contestContent["title"] = ""
    contestContent["introduction"] = ""
    contestContent["start_time"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    contestContent["end_time"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    contestContent["is_practice"] = 0
    contestContent["is_private"] = 0
    contestContent["password"] = ""
    return render_template("admin/editContest.html",contestContent=contestContent)

@bp.route("/updateContest",methods=["POST"])
def updateContest():
    db = MysqlUtils.MyPyMysqlPool()
    contestId = request.form.get("id_contest")
    contestContent = ContestServer.getContestInfo(db,contestId)
    contestContent["webTitle"] = "Update Contest"
    contestContent["start_time"] = contestContent["start_time"].strftime("%Y-%m-%dT%H:%M:%S")
    contestContent["end_time"] = contestContent["end_time"].strftime("%Y-%m-%dT%H:%M:%S")
    db.dispose()
    return render_template("admin/editContest.html",contestContent=contestContent)

@bp.route("/saveContest",methods=["POST"])
def saveContest():
    contestId = request.form.get("id_contest")
    title = request.form.get("title")
    introduction = request.form.get("introduction")
    is_practice = request.form.get("is_practice")
    is_private = request.form.get("is_private")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    password = request.form.get("password")

    error = None
    if title == None or title == "":
        error = "title is empty."
    elif introduction == None or introduction == "":
        error = "introduction is empty."
    elif start_time == None or start_time == "":
        error = "start_time is empty."
    elif end_time == None or end_time == "":
        error = "end_time is empty."

    isUpdate = False if contestId == "-1" or contestId == None else True
    if error is None:
        db = MysqlUtils.MyPyMysqlPool()
        contest = {}
        contest["id_contest"] = contestId
        contest["title"] = title
        contest["introduction"] = introduction
        contest["is_practice"] = is_practice
        contest["is_private"] = is_private
        contest["start_time"] = start_time
        contest["end_time"] = end_time
        contest["password"] = password
        contest["belong"] = session.get("id_user")
        isSuccess = False
        if isUpdate:
            isSuccess = ContestServer.updateContest(db,contest)
        else:
            isSuccess = ContestServer.insertContest(db,contest)
        if isSuccess:
            flash('{} contest successfully!'.format("Created" if isUpdate is False else "Update"),'success')
        else:
            error = "{} contest failure.".format("Created" if isUpdate is False else "Update")
            current_app.logger.error(error)
        db.dispose()

    if error is None:
        return jsonify({
            "result":"success"
        })
    flash(error,'danger')
    return jsonify({
        "result":"failure"
    })

@bp.route("/editProblemSet",methods=["POST","GET"])
def editProblemSet():
    return render_template("admin/editProblemSet.html")

@bp.route("/saveProblemSet",methods=["POST","GET"])
def saveProblemSet():
    pass

def judgeAdmin():
    if session.get('is_admin') is None:
        flash("Please log in first.",'info')
        return False
    return True