#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import session

def Paging(currentPage,totalCount,pageSize=20):
    session['pageSize'] = pageSize
    session['currentPage'] = currentPage

    total = totalCount//session.get("pageSize")
    total = total if totalCount%session.get("pageSize") == 0 or totalCount == 0 else total+1
    session['totalPage'] = total
