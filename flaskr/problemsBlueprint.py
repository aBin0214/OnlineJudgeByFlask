#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from . import MysqlUtils
from . import CodeHighlightUtils

bp = Blueprint('problems', __name__, url_prefix='/problems')

@bp.route("/problemSet/<int:currentPage>")
@bp.route("/problemSet")
def problemSet(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    g.active = 'ProblemSet'
    if session.get("contestId_pro") == 1:
        session['active'] = "Problems"
    else:
        session['active'] = "Contests"

    session['currentPage_pro'] = currentPage
    if session.get("problemTag_pro") is None:
        session["problemTag_pro"] = "All"
    if session.get("pageSize_pro") is None:
        session['pageSize_pro'] = 20
    
    totalCount = getProblemCount(db,session.get("contestId_pro"),session.get("problemTag_pro"))
    total = totalCount//session.get("pageSize_pro")
    total = total if totalCount%session.get("pageSize_pro") == 0 or totalCount == 0 else total+1
    session['totalPage_pro'] = total

    db.dispose()

    return render_template("problems/contestBase.html")

@bp.route("/ranklist/<int:currentPage>")
@bp.route("/ranklist")
def ranklist(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    g.active = 'Ranklist'
    session['currentPage_rank'] = currentPage
    if session.get("pageSize_rank") is None:
        session['pageSize_rank'] = 20

    totalCount = getRanklistCount(db,session.get("contestId_pro"))
    total = totalCount//session.get("pageSize_rank")
    total = total if totalCount%session.get("pageSize_rank") == 0 or totalCount == 0 else total+1
    session['totalPage_rank'] = total
    if totalCount == 0:
        session['totalPage_rank'] = 0

    db.dispose()

    return render_template("problems/contestBase.html")

@bp.route("/submissions/<int:currentPage>")
@bp.route("/submissions")
def submissions(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    g.active = 'Submissions'
    session['currentPage_sub'] = currentPage
    if session.get("pageSize_sub") is None:
        session['pageSize_sub'] = 20

    totalCount = getSubmissionCount(db,session.get("contestId_pro"))
    total = totalCount//session.get("pageSize_sub")
    total = total if totalCount%session.get("pageSize_sub") == 0 or totalCount == 0 else total+1
    session['totalPage_sub'] = total
    if totalCount == 0:
        session['totalPage_sub'] = 0

    db.dispose()
    
    return render_template("problems/contestBase.html")

@bp.route("/currentRanklist/<int:currentPage>")
@bp.route("/currentRanklist")
def currentRanklist(currentPage=1):
    g.active = 'Ranklist'
    return render_template("problems/contestBase.html")


@bp.route("/problemSetTag/<string:tag>")
def problemSetTag(tag):
    session['problemTag_pro'] = tag
    return redirect(url_for('problems.problemSet'))

@bp.route("/showContestInfo")
def showContestInfo():
    db = MysqlUtils.MyPyMysqlPool()
    contestInfo = getContestInfo(db,session.get("contestId_pro"))
    db.dispose()
    return render_template("problems/contestInfo.html",contestInfo = contestInfo)

@bp.route("/showProblemList")
def showProblemList():

    db = MysqlUtils.MyPyMysqlPool()

    currentPage = int(session.get("currentPage_pro"))
    problemTag = session.get("problemTag_pro")
    problems = getProblemsByTag(db,session.get("contestId_pro"),currentPage,problemTag,session.get("pageSize_pro"))
    idx = 0
    
    if problems is not False:
        for problem in problems:
            problemId = problem["id_contest_problem"]
            problems[idx]["accepted_count"] = getAcceptedCount(db,problemId)
            problems[idx]["submit_count"] = getSubmitCount(db,problemId)
            idx += 1

    db.dispose()

    return render_template("problems/problemList.html",problems = problems)

@bp.route("/showTagList")
def showTagList():
    db = MysqlUtils.MyPyMysqlPool()
    tags = getAllTag(db)
    db.dispose()
    return render_template('problems/tagList.html',tags = tags)

@bp.route("/showRanklist")
def showRanklist():
    db = MysqlUtils.MyPyMysqlPool()
    ranklist = getRanklist(db,session.get("contestId_pro"))
    db.dispose()
    return render_template("problems/ranklist.html",ranklist=ranklist)

@bp.route("/showCurRanklist")
def showCurRanklist():
    db = MysqlUtils.MyPyMysqlPool()
    serialList = getProblemSerial(db,session.get("contestId_pro"))
    db.dispose()
    return render_template("problems/curRanklist.html",serialList=serialList)

@bp.route("/showSubmissionlist")
def showSubmissionlist():
    db = MysqlUtils.MyPyMysqlPool()
    submissions = getSubmissions(db,session.get("contestId_pro"),session['currentPage_sub'],session.get("pageSize_sub"))
    db.dispose()
    return render_template("problems/submissionList.html",submissions=submissions)

@bp.route("/showSubmissionDetail/<int:solutionId>")
def showSubmissionDetail(solutionId):
    db = MysqlUtils.MyPyMysqlPool()
    submission = getOneSubmission(db,solutionId)
    db.dispose()
    if submission is not False:
        submission['hl_code'] = CodeHighlightUtils.CodeHighlight.codeTranslate(submission['submit_content'],submission['monaco_editor_val'])
    return render_template("problems/submissionDetail.html",submission=submission)

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

def getAllTag(db):
    sql = "select id_tag,name_tag,descr from tag"
    tags = None
    try:
        tags = db.get_all(sql)
    except:
        current_app.logger.error("get tags failure !")
    tags.append({'id_tag': 0, 'name_tag': 'All', 'descr': 'All Problems'})
    tags.reverse()
    return tags

def getProblemsByTag(db,contestId,currentPage,problemTag,pageSize):
    sql = ""
    start = (currentPage-1)*pageSize
    if contestId != 1 or (contestId == 1 and problemTag == "All"):
        sql = "select id_contest_problem,title,serial \
        from contest_problem,problem \
        where contest_problem.id_contest = '{id_contest}' \
        and contest_problem.id_problem = problem.id_problem\
        limit {start},{pageSize};".format(id_contest=contestId,start=start,pageSize=pageSize)
    else:
        sql = "select id_contest_problem,title,serial \
        from problem,tag,tag_problem,contest_problem \
        where contest_problem.id_contest = '{id_contest}' \
        and contest_problem.id_problem = problem.id_problem \
        and problem.id_problem = tag_problem.id_problem \
        and tag.id_tag = tag_problem.id_tag \
        and tag.name_tag = '{Tag}' limit {start},{pageSize}".format(id_contest=1,Tag=problemTag,start=start,pageSize=pageSize)
    problems = None
    try:
        problems = db.get_all(sql)
    except:
        current_app.logger.error("get problems failure !")
    return problems

def getSubmissions(db,contestId,currentPage,pageSize):
    start = (currentPage-1)*pageSize
    sql = 'select id_solution,submit_time,res.name_result as judge_status,cp.serial as problem_serial,cp.id_contest_problem,\
    lang.name_language,lang.monaco_editor_val,s.run_time,s.run_memory,u.username,u.id_user,\
    s.is_share,s.submit_content\
    from solution as s,user as u,result_des as res,\
    contest_problem as cp,pro_language as lang\
    where s.id_user = u.id_user\
    and s.state = res.id_result_des\
    and s.id_contest_problem = cp.id_contest_problem\
    and s.id_language = lang.id_language\
    and cp.id_contest = \'{id_contest}\'\
    order by s.submit_time desc\
    limit {start},{pageSize};'.format(id_contest=contestId,start=start,pageSize=pageSize);
    submissions = None
    try:
        submissions = db.get_all(sql)
    except:
        current_app.logger.error("get submissions failure !")
    return submissions

def getOneSubmission(db,solutionId):
    start = (session.get('currentPage_sub')-1)*session.get('pageSize_sub')
    sql = 'select id_solution,submit_time,res.name_result as judge_status,cp.serial as problem_serial,cp.id_contest_problem,\
    lang.name_language,lang.monaco_editor_val,s.run_time,s.run_memory,u.username,u.id_user,\
    s.is_share,s.submit_content\
    from solution as s,user as u,result_des as res,\
    contest_problem as cp,pro_language as lang\
    where s.id_user = u.id_user\
    and s.state = res.id_result_des\
    and s.id_contest_problem = cp.id_contest_problem\
    and s.id_language = lang.id_language\
    and s.id_solution = {solutionId}\
    limit 1;'.format(solutionId=solutionId);
    submission = None
    try:
        submissions = db.get_one(sql)
    except:
        current_app.logger.error("get solution-{}  failure !".format(solusionId))
    return submissions
    
def getRanklist(db,contestId):
    sql = "select u.id_user,u.username,count(distinct s.id_contest_problem) as cnt \
        from user as u,solution as s,contest_problem as cp \
        where u.id_user = s.id_user \
        and cp.id_contest_problem = s.id_contest_problem \
        and s.state = 11 \
        and cp.id_contest = '{id_contest}' \
        group by s.id_user \
        order by cnt desc;".format(id_contest=contestId)
    ranklist = None
    try:
        ranklist = db.get_all(sql)
    except:
        current_app.logger.error("get ranklist failure !")
    return ranklist

def getProblemCount(db,contestId,problemTag):
    sql = "";
    if problemTag == "All":
        sql = "select count(id_contest_problem) as cnt from contest_problem where id_contest = {contestId}".format(contestId=contestId)
    else:
        sql = "select count(contest_problem.id_contest_problem) as cnt \
        from contest_problem,problem,tag_problem,tag \
        where contest_problem.id_contest = {contestId} \
        and contest_problem.id_problem = problem.id_problem \
        and problem.id_problem = tag_problem.id_problem \
        and tag.id_tag = tag_problem.id_tag \
        and tag.name_tag = '{problemTag}' limit 1".format(contestId=1,problemTag=problemTag)
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get contest-{}'s problem count failure !".format(contestId))
    return res["cnt"]

def getSubmissionCount(db,contestId):
    sql = "select count(id_solution) as cnt \
    from solution as s,contest_problem as cp\
    where  s.id_contest_problem = cp.id_contest_problem\
    and cp.id_contest = '{id_contest}' limit 1;".format(id_contest=contestId)
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get submission count failure !")
    return res["cnt"]

def getRanklistCount(db,contestId):
    sql = "select count(distinct s.id_user) as cnt \
        from solution as s,contest_problem as cp \
        where cp.id_contest_problem = s.id_contest_problem \
        and s.state = 11 \
        and cp.id_contest = {id_contest};".format(id_contest=contestId)
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get ranklist count failure !")
    return res["cnt"]

def getAcceptedCount(db,problemId):
    sql = "select count(id_solution) as cnt \
    from solution as s,result_des as r \
    where s.state = r.id_result_des \
    and r.name_result = \"Accepted\" \
    and s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    return res["cnt"]

def getSubmitCount(db,problemId):
    sql = "select count(id_solution) as cnt \
    from solution as s \
    where s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    return res["cnt"]

def getProblemsBycontest(db,contest):
    pass

def getProblemSerial(db,contestId):
    sql = "select serial from contest_problem\
    where id_contest = {} order by serial".format(contestId)
    serialList = None
    try:
        serialList = db.get_all(sql)
    except:
        current_app.logger.error("get contest:{} problem serial list failure !".format(contestId))
    if serialList == None or serialList == False:
        return []
    return serialList

