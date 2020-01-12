#!/usr/bin/env python
# coding=utf-8

"""
__init__.py有两个作用：
一是包含应用工厂；
二是告诉Python flaskr文件夹应视作一个包
"""

import os
from flask import Flask


def create_app(test_config=None):
    """
    创建并配置app
    :param test_config:
    :return:
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev"
    )

    if test_config is None:
        # 如果不是测试，加载这个实例的配置
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载测试配置
        app.config.from_mapping(test_config)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 设置全局的注册模块
    from . import LoggerUtils
    LoggerUtils.init_logger()

    # 注册一个蓝图，用于登录和注册
    from . import auth
    app.register_blueprint(auth.bp)

    # 注册一个蓝图，用于显示网站基本信息
    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    #注册一个蓝图，用于显示题目信息
    from . import problems
    app.register_blueprint(problems.bp)

    from flask_bootstrap import Bootstrap
    bootstrap = Bootstrap(app)

    return app
