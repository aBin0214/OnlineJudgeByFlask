#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

from flaskr.utils import MysqlUtils

def saveProblemDescribe(problemId,describe):
    dirname = os.path.split(os.path.dirname(__file__))[0]
    dirname += "/problemDescribe/{}".format(problemId)
    if not os.path.exists(dirname):
        print("目录不存在，创建！")
        os.makedirs(dirname)
    with open(dirname+"/describe.md","w") as file:
        file.write(describe)

def readProblemDescribe(problemId):
    dirname = os.path.split(os.path.dirname(__file__))[0]
    dirname += "/problemDescribe/{}/describe.md".format(problemId)
    if not os.path.isfile(dirname) or not os.path.exists(dirname):
        return {
            "content":""
        }
    content = ""
    with open(dirname,"r") as file:
        content = file.read()
    return {
        "content":content
    }