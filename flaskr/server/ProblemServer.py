#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flaskr.utils import MysqlUtils

def insertProblem(db,problem):
    try:
        sql = "INSERT INTO problem (title,create_by, time_limit, mem_limit) VALUES ('{}','{}','{}','{}')" \
        .format(problem["title"], problem["create_by"],problem["time_limit"], problem["mem_limit"])
        db.insert(sql)
        return True
    except:
        current_app.logger.error("Problem insert failure !")
        return False

def updateProblem(db,problem):
    try:
        sql = "UPDATE problem SET title='{}',create_by='{}',time_limit='{}',mem_limit='{}' where id_problem = '{}'" \
        .format(problem["title"], problem["create_by"],problem["time_limit"], problem["mem_limit"],problem["id_problem"])
        db.update(sql)
        return True
    except:
        current_app.logger.error("Problem update failure !")
        return False

def getProblemById(db,problemId):
    sql = "SELECT id_problem,title,time_limit,mem_limit " \
        "FROM problem "\
        "where id_problem = {id_problem} limit 1;".format(id_problem=problemId)
    proContent = None
    try:
        proContent = db.get_one(sql)
    except:
        current_app.logger.error("get problem:{} failure !".format(problemId))
    if proContent is False or proContent is None:
        return {}
    return proContent

def getProblemCount(db):
    sql = "select count(id_problem) as cnt from problem;"
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problem count failure !")
    if res is False or res is None:
        return 0
    return res["cnt"]

def getProblemList(db,currentPage,pageSize):
    start = (currentPage-1) * pageSize
    sql = "SELECT id_problem,title,username "\
        "FROM problem,user " \
        "where problem.create_by = user.id_user limit {start},{pageSize};".format(start=start,pageSize=pageSize)
    problemList = None
    try:
        problemList = db.get_all(sql)
    except:
        current_app.logger.error("get problem list failure !")
    if problemList is False or problemList is None:
        return []
    return problemList

def getProblemAcceptedCount(db,problemId):
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

def getProblemSubmitCount(db,problemId):
    sql = "select count(id_solution) as cnt \
    from solution as s \
    where s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get problems accepted count failure !")
    return res["cnt"]

def getProblemInfo(db,idContestProblem):
    sql = "SELECT cp.serial,cp.id_contest,cp.id_contest_problem,p.id_problem,p.title as problemTitle,c.title as contestTitle,create_by,time_limit,mem_limit,username " \
        "FROM problem as p,contest_problem as cp,contest as c,user as u " \
        "where p.id_problem = cp.id_problem " \
        "and cp.id_contest = c.id_contest " \
        "and p.create_by = u.id_user " \
        "and cp.id_contest_problem = {id_contest_problem} limit 1;".format(id_contest_problem=idContestProblem)
    problemInfo = None
    try:
        problemInfo = db.get_one(sql)
    except:
        current_app.logger.info("get problem information failure !")
    if problemInfo is None or problemInfo is False:
        return {}
    return problemInfo

def getProblemTags(db,idContestProblem):
    sql = "select t.id_tag,name_tag " \
        "from tag as t ,tag_problem as tp ,contest_problem as cp " \
        "where tp.id_problem = cp.id_problem " \
        "and t.id_tag = tp.id_tag " \
        "and cp.id_contest_problem = {}".format(idContestProblem)
    problemTags = None
    try:
        problemTags = db.get_all(sql)
    except:
        current_app.logger.info("get problem tags failure !")
    if problemTags is None or problemTags is False:
        return []
    return problemTags

def getProSubmissions(db,idContestProblem):
    sql = "SELECT id_result_des,name_result,count(id_solution) as cnt "\
        "FROM online_judge.result_des as rd,online_judge.solution as s " \
        "where rd.id_result_des = s.state " \
        "and s.state not in (8,12) " \
        "and s.id_contest_problem = {} " \
        "group by rd.id_result_des".format(idContestProblem)
    proSubmissions = None
    try:
        proSubmissions= db.get_all(sql)
    except:
        current_app.logger.info("get problem submissions failure !")
    if proSubmissions is None or proSubmissions is False:
        return []
    return proSubmissions

def insertSolution(db,solution):
    try:
        sql = 'INSERT INTO solution (id_user,id_contest_problem,id_language,submit_content) VALUES (\'{}\',\'{}\',\'{}\',\'{}\')'\
        .format(solution["id_user"], solution["id_contest_problem"],solution["id_language"],solution["submit_content"])
        db.insert(sql)
        return True
    except:
        current_app.logger.error("Solution insert failure!")
        return False
