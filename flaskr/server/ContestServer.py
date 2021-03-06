#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime

from flask import current_app
from flaskr.utils import MysqlUtils

def insertContest(db,contest):
    sql = "INSERT INTO contest " \
        "(title,introduction,is_practice,is_private,start_time,end_time,password,belong) " \
        "VALUES('{}','{}','{}','{}','{}','{}','{}','{}');" \
        .format(contest["title"],contest["introduction"],contest["is_practice"],
        contest["is_private"],contest["start_time"],contest["end_time"],contest["password"],contest["belong"])
    res = 0
    try:
        res = db.insert(sql)
    except:
        current_app.logger.error("insert contest failure !")
    return True if res != 0 and res != False else False

def updateContest(db,contest):
    sql = "UPDATE contest set title='{}',introduction='{}',is_practice='{}'" \
        ",is_private='{}',start_time='{}',end_time='{}',password='{}',belong='{}' " \
        "where id_contest = {}" \
        .format(contest["title"],contest["introduction"],contest["is_practice"],
        contest["is_private"],contest["start_time"],contest["end_time"],contest["password"],contest["belong"],
        contest["id_contest"])
    try:
        db.update(sql)
        return True
    except:
        current_app.logger.error("update contest failure !")
        return False
    
def deleteContest(db,contestId):
    sql = "DELETE FROM contest WHERE id_contest = '{}';".format(contestId)
    res = 0
    try:
        res = db.delete(sql)
    except:
        current_app.logger.error("delete contest failure !")
    return True if res !=0 and res != False else False

def judgeContestProblemExist(db,contestId,problemId):
    sql = "SELECT id_contest_problem " \
        "FROM contest_problem " \
        "WHERE id_contest = '{}' AND id_problem = '{}' limit 1;".format(contestId,problemId)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("judge contest problem exist failure !")
    if res is None or res is False:
        return True
    return False

def insertContestProblem(db,contestId,problemId):
    sql = "INSERT INTO contest_problem " \
    "(id_contest,id_problem)" \
    "VALUES('{}','{}'); ".format(contestId,problemId)
    res = 0
    try:
        res = db.insert(sql)
    except:
        current_app.logger.error("insert contest problem failure !")
    return True if res != 0 and res != False else False

def updateContestProblem(db,contestProblemId,problemId):
    sql = "UPDATE contest_problem " \
          "SET id_problem = '{}' " \
          "WHERE id_contest_problem = '{}';".format(problemId,contestProblemId)
    res = 0
    try:
        res = db.update(sql)
    except:
        current_app.logger.error("update contest problem failure !")
    return True if res != 0 and res != False else False

def deleteContestProblem(db,contestProblemId):
    sql = "DELETE FROM contest_problem " \
        "WHERE id_contest_problem = '{}';".format(contestProblemId)
    res = 0
    try:
        res = db.delete(sql)
    except:
        current_app.logger.error("delete contest problem failure !")
    return True if res != 0 and res != False else False

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
        sql = "select id_contest_problem,title,problem.id_problem \
        from contest_problem,problem \
        where contest_problem.id_contest = '{id_contest}' \
        and contest_problem.id_problem = problem.id_problem\
        limit {start},{pageSize};".format(id_contest=contestId,start=start,pageSize=pageSize)
    else:
        sql = "select id_contest_problem,title,problem.id_problem \
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
    sql = 'select id_solution,submit_time,res.name_result as judge_status,cp.id_problem,cp.id_contest_problem,\
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
    sql = 'select id_solution,submit_time,res.name_result as judge_status,cp.id_problem,cp.id_contest_problem,\
    lang.name_language,lang.monaco_editor_val,compile_result,s.run_time,s.run_memory,u.username,u.id_user,\
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
        submission = db.get_one(sql)
    except:
        current_app.logger.error("get solution-{}  failure !".format(solusionId))
    if submission is None or submission is False:
        return {}
    return submission
    
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

def getCurRanklist(db,contestId):
    sql = "select id_solution,u.id_user,u.username,cp.id_contest_problem,state,c.start_time,s.submit_time " \
    "from online_judge.solution as s,online_judge.contest_problem as cp, " \
    "online_judge.contest as c,online_judge.user as u " \
    "where cp.id_contest_problem = s.id_contest_problem " \
    "and cp.id_contest = c.id_contest " \
    "and s.id_user = u.id_user " \
    "and s.submit_time >= c.start_time " \
    "and s.submit_time <= c.end_time " \
    "and cp.id_contest = '{}' " \
    "order by s.submit_time".format(contestId)
    contestSolutionList = None
    try:
        contestSolutionList = db.get_all(sql)
    except:
        current_app.logger.error("get contest-{} solution list failure !".format(contestId))
    if contestSolutionList is None or contestSolutionList is False:
        return []
    userRank = {}
    #统计出比赛的实时排名
    for solution in contestSolutionList:
        userState = userRank.setdefault(solution['id_user'],{"username":solution['username'],"solveCnt":0,"time":0,"probs":{}})
        if solution["state"] in [7,8,12]:#表示系统错误，队列中，提交状态
            continue
        userProb = userState["probs"].setdefault(solution["id_contest_problem"],{"wrongCnt":0,"successTime":None,"duration":None})
        if solution['state'] == 11:#如果Accepted
            seconds = (solution["submit_time"]-solution["start_time"]).total_seconds()
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            if userProb["successTime"] is None:
                userProb["successTime"] = solution["submit_time"]
                userProb["duration"] = "{hours}:{minutes}:{seconds}".format(hours=str(int(hours)).zfill(2),minutes=str(int(minutes)).zfill(2),seconds=str(int(seconds)).zfill(2))
                userState["time"] += userProb["wrongCnt"]*20
                userState["time"] += max(0,round((solution["submit_time"]-solution["start_time"]).total_seconds()/60))
                userState['solveCnt'] += 1
            elif solution["submit_time"] < userProb["successTime"]:
                userProb["duration"] = "{hours}:{minutes}:{seconds}".format(hours=str(int(hours)).zfill(2),minutes=str(int(minutes)).zfill(2),seconds=str(int(seconds)).zfill(2))
                userState["time"] -= max(0,round((userProb["successTime"]-solution["start_time"]).total_seconds()/60))
                userProb["successTime"] = solution["submit_time"]
        else:
            if userProb["successTime"] is None:
                userProb["wrongCnt"] += 1
            elif solution["submit_time"] < userProb["successTime"]:
                userProb["wrongCnt"] += 1
                userState["time"] += 20
    #对计算好的排名结果进行排序
    curRankList = []
    for userId in userRank.keys():
        userRank[userId].setdefault("id_user",userId)
        curRankList.append(userRank[userId])
    for i in range(len(curRankList)):
        for j in range(i+1,len(curRankList)):
            if curRankList[i]["solveCnt"] < curRankList[j]["solveCnt"] or (curRankList[i]["solveCnt"] == curRankList[j]["solveCnt"] and curRankList[i]["time"] > curRankList[j]["time"]):
                tmp = curRankList[j]
                curRankList[j] = curRankList[i]
                curRankList[i] = tmp
    idx = 1
    for rankItem in curRankList:
        rankItem["rank"] = idx
        idx += 1
    return curRankList

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

#获取contest里已经存在的problem
def getExistingProblems(db,contestId):
    sql = "SELECT id_contest_problem,id_contest,id_problem " \
    "FROM online_judge.contest_problem " \
    "WHERE id_contest = '{}';".format(contestId)
    existingProblems = None
    try:
        existingProblems = db.get_all(sql)
    except:
        current_app.logger.error("get contest existing problems failure !")
    if existingProblems is None or existingProblems is False:
        return []
    return existingProblems
