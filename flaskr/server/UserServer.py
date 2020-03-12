#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime

from flaskr.utils import MysqlUtils
from werkzeug.security import check_password_hash, generate_password_hash

def isAlreadyRegister(db,username):
    sql = "SELECT id_user FROM user WHERE username = '{}' limit 1;".format(username)
    res = None
    try:
        db.get_one(sql)
    except:
        current_app.logger.error("Judge user already register failure !")
    if res is None or res is False:
        return False
    return True

def userRegister(db,username,password):
    sql = "INSERT INTO user (username, password, is_admin) VALUES ('{}','{}','{}')"\
        .format(username, generate_password_hash(password), 0)
    row = 0
    try:
        row = db.insert(sql)
    except:
        current_app.logger.error("User register failure !")
    return True if row != 0 else False

def getUser(db,userId=None,username=None):
    sql = ""
    if userId is not None:
        sql = "SELECT id_user,username,password,is_admin FROM user WHERE id_user = '{}' limit 1".format(userId)
    elif username is not None:
        sql = "SELECT id_user,username,password,is_admin FROM user WHERE username = '{}' limit 1".format(username)
    else:
        return {}
    user = None
    try:
        user = db.get_one(sql)
    except:
        current_app.logger.error("Get User failure !")
    if user is None or user is False:
        return {}
    return user

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

def getUserInfo(db,userId):
    sql = "select id_user,username,password,is_admin from user\
    where id_user = {id_user} limit 1;".format(id_user=userId)
    userInfo = None
    try:
        userInfo = db.get_one(sql)
    except:
        current_app.logger.error("get user:{} information failure !".format(userId))
    if userInfo is None or userInfo is False:
        return {}
    return userInfo

def getUserProCount(db,userId,interval=-1,state=-1):
    stateStr = ""
    if state != -1:
        stateStr = "and s.state = {}".format(state)
    intervalStr = ""
    if interval != -1:
        intervalStr = "and s.submit_time > '{}'".format(
            (datetime.datetime.now()+datetime.timedelta(days=interval)).strftime("%Y-%m-%d %H:%M:%S")
        )

    sql = "select count(DISTINCT cp.id_problem) as cnt \
            from solution as s,contest_problem as cp \
            where s.id_contest_problem = cp.id_contest_problem \
            and id_user = {id_user} \
            {state}\
            {time}\
            limit 1".format(id_user=userId,state=stateStr,time=intervalStr)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user count failure !")
    if res is False or res is None:
        return 0
    return res['cnt']

def getUserProList(db,userId,isSolved=True):
    sql = ""
    if isSolved:
        sql = "select distinct cp.id_problem,cp.id_contest_problem\
            from solution as s,contest_problem as cp\
            where s.id_contest_problem = cp.id_contest_problem\
            and s.id_user = {id_user}\
            and s.state = 11\
            order by s.submit_time".format(id_user=userId)
    else:
        sql = "select distinct cp.id_problem,cp.id_contest_problem\
            from online_judge.solution as s,online_judge.contest_problem as cp\
            where s.id_contest_problem = cp.id_contest_problem\
            and id_user = {id_user}\
            and cp.id_problem not in (select distinct cp.id_problem\
            from online_judge.solution as s,online_judge.contest_problem as cp\
            where s.id_contest_problem = cp.id_contest_problem\
            and id_user = {id_user}\
            and s.state = 11)\
            order by s.submit_time".format(id_user=userId)
        pass
    solvedPro = None
    try:
        solvedPro = db.get_all(sql)
    except:
        current_app.logger.error("get user:{} {} problem failure !".format(userId,"solved" if isSolved else "unsolved"))
    if solvedPro is None or solvedPro is False:
        return []
    return solvedPro

def getUserSubmitCount(db,userId,startTime,endTime):
    sql = "select count(id_solution) as cnt from solution \
    where id_user = {id_user}\
    and submit_time >= '{startTime}'\
    and submit_time < '{endTime}';".format(id_user=userId,startTime=startTime,endTime=endTime)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user submit count failure !")
    if res is False or res is None:
        return 0
    return res['cnt']

def getUserAttemptedCount(db,userId,startTime,endTime):
    sql = "select count(distinct id_contest_problem) as cnt from solution \
    where id_user = {id_user}\
    and submit_time >= '{startTime}'\
    and submit_time < '{endTime}';".format(id_user=userId,startTime=startTime,endTime=endTime)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user attempted count failure !")
    if res is False or res is None:
        return 0
    return res['cnt']

def getUserAcceptedCount(db,userId,startTime,endTime):
    sql = "select count(distinct id_contest_problem) as cnt from solution \
    where state = 11\
    and id_user = {id_user}\
    and submit_time >= '{startTime}'\
    and submit_time < '{endTime}';".format(id_user=userId,startTime=startTime,endTime=endTime)
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("get user accept count failure !")
    if res is False or res is None:
        return 0
    return res['cnt']

    