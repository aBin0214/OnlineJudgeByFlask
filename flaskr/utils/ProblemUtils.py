#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import shutil

from flaskr.utils import MysqlUtils

def saveProblemDescribe(problemId,describe):
    dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
    dirname += "/problemDescribe/{}".format(problemId)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(dirname+"/describe.md","w") as file:
        file.write(describe)

def readProblemDescribe(problemId):
    dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
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

def readProblemData(problemId):
    dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
    dirname += "/compile/problem/{}/".format(problemId)
    if not os.path.exists(dirname):
        return []
    files = os.listdir(dirname)
    idx = 1
    dataMap = {}
    for item in files:
        idx = item[5]
        data = dataMap.setdefault(int(item[5]),{"input":"","output":""})
        if item.endswith(".in") and item.startswith("data"):
            with open(dirname+item,'r') as file:
                data["input"] = file.read()
        if item.endswith(".out") and item.startswith("data"):
            with open(dirname+item,'r') as file:
                data["output"] = file.read()
    dataList = []
    for key in dataMap.keys():
        dataMap[key]['serial'] = key
        dataList.append(dataMap[key])
    for i in range(len(dataList)):
        for j in range(i+1,len(dataList)):
            if dataList[i]["serial"] > dataList[j]["serial"]:
                tmp = dataList[i]
                dataList[i] = dataList[j]
                dataList[j] = tmp
    return dataList

def updateProblemData(problemId,idx,inOut,content):
    dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
    dirname += "/compile/problem/{}/".format(problemId)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = dirname + "data_{}.{}".format(idx,"in" if inOut is True else "out")
    with open(filename,'w') as file:
        file.write(content)

# def deleteProblemData(problemId,idx):
#     dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
#     dirname += "/compile/problem/{}/".format(problemId)
#     if not os.path.exists(dirname):
#         return 
#     inputName = dirname + "data_{}.in".format(idx)
#     outputName = dirname + "data_{}.out".format(idx)
#     if os.path.exists(inputName):
#         os.remove(inputName)
#     if os.path.exists(outputName):
#         os.remove(outputName)

def deleteProblemData(problemId):
    dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
    dirname += "/compile/problem/{}/".format(problemId)
    if os.path.exists(dirname):
        shutil.rmtree(dirname, ignore_errors=True)