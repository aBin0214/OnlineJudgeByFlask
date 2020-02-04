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
    if session.get("contestId_pro") == 1:
        session['active'] = "Problems"
    else:
        session['active'] = "Contests"

    session['currentPage_pro'] = currentPage
    if session.get("problemTag_pro") is None:
        session["problemTag_pro"] = "All"
    if session.get("pageSize_pro") is None:
        session['pageSize_pro'] = 20
    
    totalCount = getProblemCount(session.get("contestId_pro"),session.get("problemTag_pro"))
    total = totalCount//session.get("pageSize_pro")
    total = total if totalCount%session.get("pageSize_pro") == 0 or totalCount == 0 else total+1
    session['totalPage_pro'] = total

    currentPage = int(session.get("currentPage_pro"))
    problemTag = session.get("problemTag_pro")
    problems = getProblemsByTag(session.get("contestId_pro"),currentPage,problemTag,session.get("pageSize_pro"))
    idx = 0
    
    if problems is not False:
        for problem in problems:
            problemId = problem["id_contest_problem"]
            problems[idx]["accepted_count"] = getAcceptedCount(problemId)
            problems[idx]["submit_count"] = getSubmitCount(problemId)
            idx += 1
    
    tags = getAllTag()
    contestInfo = getContestInfo(session.get("contestId_pro"))

    return render_template("problems/problemSet.html",problems=problems,tags = tags,contestInfo = contestInfo,datetime=datetime.datetime)

@bp.route("/ranklist/<int:currentPage>")
@bp.route("/ranklist")
def ranklist(currentPage=1):
    session['currentPage_rank'] = currentPage
    if session.get("pageSize_rank") is None:
        session['pageSize_rank'] = 20

    totalCount = getRanklistCount(session.get("contestId_pro"))
    total = totalCount//session.get("pageSize_rank")
    total = total if totalCount%session.get("pageSize_rank") == 0 or totalCount == 0 else total+1
    session['totalPage_rank'] = total
    if totalCount == 0:
        session['totalPage_rank'] = 0

    contestInfo = getContestInfo(session.get("contestId_pro"))
    ranklist = getRanklist(session.get("contestId_pro"))

    return render_template("problems/ranklist.html",contestInfo = contestInfo,ranklist=ranklist)


@bp.route("/submissions/<int:currentPage>")
@bp.route("/submissions")
def submissions(currentPage=1):
    session['currentPage_sub'] = currentPage
    if session.get("pageSize_sub") is None:
        session['pageSize_sub'] = 20

    totalCount = getSubmissionCount(session.get("contestId_pro"))
    total = totalCount//session.get("pageSize_sub")
    total = total if totalCount%session.get("pageSize_sub") == 0 or totalCount == 0 else total+1
    session['totalPage_sub'] = total
    if totalCount == 0:
        session['totalPage_sub'] = 0

    contestInfo = getContestInfo(session.get("contestId_pro"))
    
    submissions = getSubmissions(session.get("contestId_pro"),currentPage,session.get("pageSize_sub"))

    if submissions is not False:
        for submission in submissions:
            submission['hl_code'] = CodeHighlightUtils.CodeHighlight.codeTranslate(submission['submit_content'],submission['monaco_editor_val']);

    return render_template("problems/submissions.html",contestInfo = contestInfo,submissions=submissions)

@bp.route("/problemSetTag/<string:tag>")
def problemSetTag(tag):
    session['problemTag_pro'] = tag
    return redirect(url_for('problems.problemSet'))

def getContestInfo(id_contest):
    db = MysqlUtils.MyPyMysqlPool()
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
    finally:
        db.dispose()
    return contestInfo

def getAllTag():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select id_tag,name_tag,descr from tag"
    tags = None
    try:
        tags = db.get_all(sql)
    except:
        current_app.logger.error("get tags failure !")
    finally:
        db.dispose()
    tags.append({'id_tag': 0, 'name_tag': 'All', 'descr': 'All Problems'})
    tags.reverse()
    return tags

def getProblemsByTag(contestId,currentPage,problemTag,pageSize):
    db = MysqlUtils.MyPyMysqlPool()
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
    finally:
        db.dispose()
    return problems

def getSubmissions(contestId,currentPage,pageSize):
    db = MysqlUtils.MyPyMysqlPool()
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
    finally:
        db.dispose()
    return submissions
    
def getRanklist(contestId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select u.id_user,u.username,count(distinct s.id_contest_problem) as cnt \
        from online_judge.user as u,online_judge.solution as s,online_judge.contest_problem as cp \
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
    finally:
        db.dispose()
    return ranklist

def getProblemCount(contestId,problemTag):
    db = MysqlUtils.MyPyMysqlPool()
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
    finally:
        db.dispose()
    return res["cnt"]

def getSubmissionCount(contestId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(id_solution) as cnt \
    from solution as s,contest_problem as cp\
    where  s.id_contest_problem = cp.id_contest_problem\
    and cp.id_contest = '{id_contest}' limit 1;".format(id_contest=contestId)
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get submission count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getRanklistCount(contestId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(distinct s.id_user) as cnt \
        from solution as s,contest_problem as cp \
        where cp.id_contest_problem = s.id_contest_problem \
        and s.state = 11 \
        and cp.id_contest = {id_contest};".format(id_contest=contestId)
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get ranklist count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getAcceptedCount(problemId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(id_solution) as cnt \
    from solution as s,result_des as r \
    where s.state = r.id_result_des \
    and r.name_result = \"Accepted\" \
    and s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getSubmitCount(problemId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(id_solution) as cnt \
    from solution as s \
    where s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getProblemsBycontest(contest):
    pass

