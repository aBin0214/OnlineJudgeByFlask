#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session,jsonify,current_app
)
from werkzeug.exceptions import abort
import datetime
from pyecharts import options as opts
from pyecharts.charts import Bar
from jinja2 import Markup
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType   

from flaskr.utils import MysqlUtils

from flaskr.server import UserServer

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/userIndex/<int:userId>")
@bp.route("/userIndex")
def userIndex(userId=-1):
    if userId == -1 and session.get("id_user") is not None:
        userId = session.get("id_user")
    g.userId = userId
    return render_template("user/userIndex.html")

@bp.route("/profile",methods=['POST'])
def profile():
    db = MysqlUtils.MyPyMysqlPool()

    userId = request.form.get("userId")
    userInfo = UserServer.getUserInfo(db,userId)

    proCnt = {
        "24hours":0,
        "7days":0,
        "30days":0,
        "OverallSolved":0,
        "OverallAttempted":0
    }
    proCnt["24hours"] = UserServer.getUserProCount(db,userId,1,11)
    proCnt["7days"] = UserServer.getUserProCount(db,userId,7,11)
    proCnt["30days"] = UserServer.getUserProCount(db,userId,30,11)
    proCnt["OverallSolved"] = UserServer.getUserProCount(db,userId,-1,11)
    proCnt["OverallAttempted"] = UserServer.getUserProCount(db,userId,-1,-1)

    db.dispose()

    return render_template("user/profile.html",userInfo=userInfo,proCnt=proCnt)

@bp.route("/detail",methods=['POST'])
def detail():
    db = MysqlUtils.MyPyMysqlPool()

    userId = request.form.get("userId")
    solvedList = UserServer.getUserProList(db,userId)
    failedList = UserServer.getUserProList(db,userId,False)
    if solvedList is False or solvedList is None:
        solvedList = {}
    if failedList is False or failedList is None:
        failedList = {}

    db.dispose()
    return render_template("user/detail.html",solvedList=solvedList,failedList=failedList)

@bp.route("/report",methods=['POST'])
def report():
    userId = request.form.get("userId")
    db = MysqlUtils.MyPyMysqlPool()
    graph = getStatisticsGraph(db,userId)
    db.dispose()
    return Markup(graph.render_embed())

@bp.route("/showUpdate")
def showUpdate():
    return render_template("user/updateUser.html")

def getStatisticsGraph(db,userId):
    nowTime =datetime.datetime.now()
    dateList = []
    submitList = []
    attemptedList = []
    acceptList = []

    startTime = datetime.datetime(nowTime.year,nowTime.month,nowTime.day,0,0,0)
    endTime  = datetime.datetime(nowTime.year,nowTime.month,nowTime.day,23,59,59)
    for idx in range(7):
        startTimeTmp = startTime + datetime.timedelta(days=-1*idx)
        endTimeTmp = endTime + datetime.timedelta(days=-1*idx)
        dateList.append("{}.{}".format(startTimeTmp.month,endTimeTmp.day))
        submitList.append(UserServer.getUserSubmitCount(db,userId,startTimeTmp,endTimeTmp))
        attemptedList.append(UserServer.getUserAttemptedCount(db,userId,startTimeTmp,endTimeTmp))
        acceptList.append(UserServer.getUserAcceptedCount(db,userId,startTimeTmp,endTimeTmp))
    dateList.reverse()
    submitList.reverse()
    attemptedList.reverse()
    acceptList.reverse()

    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width="1200px", height="500px"))
            .add_xaxis(dateList)
            .add_yaxis("Submittimes", submitList)
            .add_yaxis("Attempted Problems", attemptedList)
            .add_yaxis("Accept Problems", acceptList)
            .set_global_opts(title_opts=opts.TitleOpts(title="Statistics", subtitle="Last 7 days"),
            yaxis_opts=opts.AxisOpts(min_interval=1))
    )
    return bar
