#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from flaskr.utils import MysqlUtils

def insertContest(db,contest):
    sql = "INSERT INTO contest " \
        "(title,introduction,is_practice,is_private,start_time,end_time,password,belong) " \
        "VALUES('{}','{}','{}','{}','{}','{}','{}','{}');" \
        .format(contest["title"],contest["introduction"],contest["is_practice"],
        contest["is_private"],contest["start_time"],contest["end_time"],contest["password"],contest["belong"])
    print(sql)
    try:
        res = db.insert(sql)
        return True
    except:
        current_app.logger.error("insert contest failure !")
        return False

def updateContest(db,contest):
    sql = "UPDATE contest set title='{}',introduction='{}',is_practice='{}'" \
        ",is_private='{}',start_time='{}',end_time='{}',password='{}',belong='{}' " \
        "where id_contest = {}" \
        .format(contest["title"],contest["introduction"],contest["is_practice"],
        contest["is_private"],contest["start_time"],contest["end_time"],contest["password"],contest["belong"],
        contest["id_contest"])
    print(sql)
    try:
        res = db.update(sql)
        return True
    except:
        current_app.logger.error("insert contest failure !")
        return False

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

def getContestList(db,currentPage,pageSize):
    start = (currentPage-1) * pageSize
    sql = "SELECT id_contest,title,introduction,start_time,end_time," \
    "is_practice,belong,is_private,password FROM contest limit {start},{pageSize};".format(start=start,pageSize=pageSize)
    contestList = None
    try:
        contestList = db.get_all(sql)
    except:
        current_app.logger.error("get contest list failure !")
    if contestList is False or contestList is None:
        return []
    return contestList

def getContestInfo(db,id_contest):
    sql = "SELECT id_contest,title,introduction,start_time,end_time,is_practice,username as belong,is_private,user.password \
        FROM contest,user \
        where contest.belong = user.id_user \
        and id_contest = {id_contest} \
        limit 1".format(id_contest=id_contest)
    contestInfo = None
    try:
        contestInfo = db.get_one(sql)
    except:
        current_app.logger.error("get contest infomation failure !")
    if contestInfo is None or contestInfo is False:
        return {}
    return contestInfo

def getAllTag(db):
    sql = "select id_tag,name_tag,descr from tag"
    tags = None
    try:
        tags = db.get_all(sql)
    except:
        current_app.logger.error("get tags failure !")
    if tags is None or tags is False:
        tags = []
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

    if problems is None or problems is False:
        return []
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
    if submissions is None or submissions is False:
        return []
    return submissions

def getOneSubmission(db,solutionId):
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
    if submission is None or submission is False:
        return []
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
    if ranklist is None or ranklist is False:
        return []
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
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get submission count failure !")
    if res is None or res is False:
        return 0
    return res["cnt"]

def getRanklistCount(db,contestId):
    sql = "select count(distinct s.id_user) as cnt \
        from solution as s,contest_problem as cp \
        where cp.id_contest_problem = s.id_contest_problem \
        and s.state = 11 \
        and cp.id_contest = {id_contest};".format(id_contest=contestId)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get ranklist count failure !")
    if res is None or res is False:
        return 0
    return res["cnt"]

def getAcceptedCount(db,problemId):
    sql = "select count(id_solution) as cnt \
    from solution as s,result_des as r \
    where s.state = r.id_result_des \
    and r.name_result = \"Accepted\" \
    and s.id_contest_problem = {}".format(problemId)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    if res is None or res is False:
        return 0
    return res["cnt"]

def getSubmitCount(db,problemId):
    sql = "select count(id_solution) as cnt \
    from solution as s \
    where s.id_contest_problem = {}".format(problemId)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    if res is None or res is False:
        return 0
    return res["cnt"]

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

