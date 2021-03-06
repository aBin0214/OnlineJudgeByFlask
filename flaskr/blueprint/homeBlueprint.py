#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
)
from werkzeug.exceptions import abort

from flaskr.utils import MysqlUtils
from flaskr.utils import CodeHighlightUtils

from flaskr.server import CompileServer

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
    db = MysqlUtils.MyPyMysqlPool()
    compileInfo = CompileServer.getCompileInfo(db)
    db.dispose()
    return render_template("home/compilers.html",compileInfo=compileInfo)

@bp.route("/showAJR")
def showAJR():
    db = MysqlUtils.MyPyMysqlPool()
    resultsDes = CompileServer.getResultDes(db)
    db.dispose()
    return render_template("home/judgeResult.html",resultsDes=resultsDes)

@bp.route("/showAJ")
def showAJ():
    return render_template("home/java.html")

