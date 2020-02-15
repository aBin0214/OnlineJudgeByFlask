#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
)
from werkzeug.exceptions import abort

from flaskr.authBlueprint import login_required
from . import MysqlUtils
from . import CodeHighlightUtils

bp = Blueprint('home', __name__)

codeList = {
"cpp":r"""
#include <iostream>
using namespace std;

int main()
{
    int a,b;
    while(cin >> a>> b)
    cout << a+b << endl;
}
""",
"c":r"""
#include <stdio.h>
int main()
{
    int a,b;
    while(scanf("%d %d",&a, &b) != EOF)
    printf("%d\n",a+b);
    return 0;
}
""",
"java":r"""
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        while (in.hasNextInt()) {
                int a = in.nextInt();
                int b = in.nextInt();
                System.out.println(a + b);
        }
    }
}
""",
"python2":r"""
import sys
for line in sys.stdin:
    a = line.split()
    print int(a[0]) + int(a[1])
""",
"python3":r"""
import sys
for line in sys.stdin:
    a = line.split()
    print(int(a[0]) + int(a[1]))
"""
}

@bp.route("/")
def index():
    session['active'] = "Home"
    return render_template("home/home.html")

@bp.route("/showIO")
def showIO():
    codeMap = {}
    for key in codeList:
        lang = key
        if key == "python2" or key == "python3":
            lang = "python"
        codeMap[key] = CodeHighlightUtils.CodeHighlight.codeTranslate(codeList[key],lang)
    return render_template("home/codeExample.html",codeMap=codeMap)

@bp.route("/showAC")
def showAC():
    compileInfo = getCompileInfo()
    return render_template("home/compilers.html",compileInfo=compileInfo)

@bp.route("/showAJR")
def showAJR():
    resultsDes = getResultDes()
    return render_template("home/judgeResult.html",resultsDes=resultsDes)

@bp.route("/showAJ")
def showAJ():
    return render_template("home/java.html")

def getCompileInfo():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "SELECT name_language,version,cmd FROM pro_language;"
    compileInfo = None
    try:
        compileInfo = db.get_all(sql)
    except:
        current_app.logger.info("get compile information failure !")
    finally:
        db.dispose()
    return compileInfo

def getResultDes():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "SELECT name_result,description FROM result_des;"
    resultsDes = None
    try:
        resultsDes = db.get_all(sql)
    except:
        current_app.logger.info("get result description failure !")
    finally:
        db.dispose()
    return resultsDes

