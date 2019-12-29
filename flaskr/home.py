#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from . import mysql_DBUtils

bp = Blueprint('home', __name__)


@bp.route("/")
def index():
    return render_template("home/home.html")

