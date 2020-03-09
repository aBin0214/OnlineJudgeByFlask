#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from flaskr.utils import MysqlUtils
from flaskr.utils import CodeHighlightUtils
from flaskr.utils import PagingUtils

from flaskr.server import ContestServer
from flaskr.server import ProblemServer

bp = Blueprint('contestDetail', __name__, url_prefix='/contestDetail')

@bp.route("/problemSet")
def problemSet():
    if session.get("contestId") == 1:
        session['active'] = "Problems"
    else:
        session['active'] = "Contests"

    db = MysqlUtils.MyPyMysqlPool()
    contestInfo = ContestServer.getContestInfo(db,session.get("contestId"))
    db.dispose()

    return render_template("contestDetail/contestBase.html",contestInfo=contestInfo)

@bp.route("/problemSetTag/<string:tag>")
def problemSetTag(tag):
    session['problemTag'] = tag
    return redirect(url_for('contestDetail.problemSet'))

@bp.route("/showProblemList")
@bp.route("/showProblemList/<int:currentPage>")
def showProblemList(currentPage=1):

    if session.get("problemTag") is None:
        session["problemTag"] = "All"

    db = MysqlUtils.MyPyMysqlPool()

    PagingUtils.Paging(currentPage,ContestServer.getProblemCount(db,session.get("contestId"),session.get("problemTag")))

    problemTag = session.get("problemTag")
    problems = ContestServer.getProblemsByTag(db,session.get("contestId"),currentPage,problemTag,session.get("pageSize"))
    idx = 0
    
    if problems is not False:
        for problem in problems:
            problemId = problem["id_contest_problem"]
            problems[idx]["accepted_count"] = ProblemServer.getProblemAcceptedCount(db,problemId)
            problems[idx]["submit_count"] = ProblemServer.getProblemSubmitCount(db,problemId)
            idx += 1

    db.dispose()

    return render_template("contestDetail/problemList.html",problems = problems)

@bp.route("/showTagList")
def showTagList():
    db = MysqlUtils.MyPyMysqlPool()
    tags = ContestServer.getAllTag(db)
    db.dispose()
    return render_template('contestDetail/tagList.html',tags = tags)

@bp.route("/showRanklist")
@bp.route("/showRanklist/<int:currentPage>")
def showRanklist(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    PagingUtils.Paging(currentPage,ContestServer.getRanklistCount(db,session.get("contestId")))
    ranklist = ContestServer.getRanklist(db,session.get("contestId"))
    db.dispose()
    return render_template("contestDetail/ranklist.html",ranklist=ranklist)

@bp.route("/showCurRanklist")
def showCurRanklist():
    db = MysqlUtils.MyPyMysqlPool()
    serialList = ContestServer.getProblemSerial(db,session.get("contestId"))
    db.dispose()
    return render_template("contestDetail/curRanklist.html",serialList=serialList)

@bp.route("/showSubmissionList")
@bp.route("/showSubmissionList/<int:currentPage>")
def showSubmissionList(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    PagingUtils.Paging(currentPage,ContestServer.getSubmissionCount(db,session.get("contestId")))
    submissions = ContestServer.getSubmissions(db,session.get("contestId"),session['currentPage'],session.get("pageSize"))
    db.dispose()
    return render_template("contestDetail/submissionList.html",submissions=submissions)

@bp.route("/showSubmissionDetail/<int:solutionId>")
def showSubmissionDetail(solutionId):
    db = MysqlUtils.MyPyMysqlPool()
    submission = ContestServer.getOneSubmission(db,solutionId)
    print(submission)
    db.dispose()
    if submission is not False:
        submission['hl_code'] = CodeHighlightUtils.CodeHighlight.codeTranslate(submission['submit_content'],submission['monaco_editor_val'])
    return render_template("contestDetail/submissionDetail.html",submission=submission)
