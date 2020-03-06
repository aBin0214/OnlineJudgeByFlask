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

bp = Blueprint('contestDetail', __name__, url_prefix='/contestDetail')

@bp.route("/problemSet")
def problemSet():
    if session.get("contestId") == 1:
        session['active'] = "Problems"
    else:
        session['active'] = "Contests"

    db = MysqlUtils.MyPyMysqlPool()
    contestInfo = getContestInfo(db,session.get("contestId"))
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

    PagingUtils.Paging(currentPage,getProblemCount(db,session.get("contestId"),session.get("problemTag")))

    problemTag = session.get("problemTag")
    problems = getProblemsByTag(db,session.get("contestId"),currentPage,problemTag,session.get("pageSize"))
    idx = 0
    
    if problems is not False:
        for problem in problems:
            problemId = problem["id_contest_problem"]
            problems[idx]["accepted_count"] = getAcceptedCount(db,problemId)
            problems[idx]["submit_count"] = getSubmitCount(db,problemId)
            idx += 1

    db.dispose()

    return render_template("contestDetail/problemList.html",problems = problems)

@bp.route("/showTagList")
def showTagList():
    db = MysqlUtils.MyPyMysqlPool()
    tags = getAllTag(db)
    db.dispose()
    return render_template('contestDetail/tagList.html',tags = tags)

@bp.route("/showRanklist")
@bp.route("/showRanklist/<int:currentPage>")
def showRanklist(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    PagingUtils.Paging(currentPage,getRanklistCount(db,session.get("contestId")))
    ranklist = getRanklist(db,session.get("contestId"))
    db.dispose()
    return render_template("contestDetail/ranklist.html",ranklist=ranklist)

@bp.route("/showCurRanklist")
def showCurRanklist():
    db = MysqlUtils.MyPyMysqlPool()
    serialList = getProblemSerial(db,session.get("contestId"))
    db.dispose()
    return render_template("contestDetail/curRanklist.html",serialList=serialList)

@bp.route("/showSubmissionList")
@bp.route("/showSubmissionList/<int:currentPage>")
def showSubmissionList(currentPage=1):
    db = MysqlUtils.MyPyMysqlPool()
    PagingUtils.Paging(currentPage,getSubmissionCount(db,session.get("contestId")))
    submissions = getSubmissions(db,session.get("contestId"),session['currentPage'],session.get("pageSize"))
    db.dispose()
    return render_template("contestDetail/submissionList.html",submissions=submissions)

@bp.route("/showSubmissionDetail/<int:solutionId>")
def showSubmissionDetail(solutionId):
    db = MysqlUtils.MyPyMysqlPool()
    submission = getOneSubmission(db,solutionId)
    db.dispose()
    if submission is not False:
        submission['hl_code'] = CodeHighlightUtils.CodeHighlight.codeTranslate(submission['submit_content'],submission['monaco_editor_val'])
    return render_template("contestDetail/submissionDetail.html",submission=submission)

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
        from problem,tag,tagblem,contest_problem \
        where contest_problem.id_contest = '{id_contest}' \
        and contest_problem.id_problem = problem.id_problem \
        and problem.id_problem = tagblem.id_problem \
        and tag.id_tag = tagblem.id_tag \
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
    sql = ""
    if problemTag == "All":
        sql = "select count(id_contest_problem) as cnt from contest_problem where id_contest = {contestId}".format(contestId=contestId)
    else:
        sql = "select count(contest_problem.id_contest_problem) as cnt \
        from contest_problem,problem,tagblem,tag \
        where contest_problem.id_contest = {contestId} \
        and contest_problem.id_problem = problem.id_problem \
        and problem.id_problem = tagblem.id_problem \
        and tag.id_tag = tagblem.id_tag \
        and tag.name_tag = '{problemTag}' limit 1".format(contestId=1,problemTag=problemTag)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get contest-{}'s problem count failure !".format(contestId))
    if res is None or res is False:
        return 0
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

