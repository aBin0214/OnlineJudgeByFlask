#!/usr/bin/env python
# -*- coding:utf-8 -*-

import wtforms # 定义字段
from flask_wtf import FlaskForm # 定义表单
from wtforms import validators # 定义校验

class UserFrom(FlaskForm):
    """
    form字段的参数
    label=None, 表单的标签
    validators=None, 校验，传入校验的方法
    filters=tuple(), 过滤
    description='',  描述
    id=None, html id
    default=None, 默认值
    widget=None, HTML样式
    render_kw=None, HTML属性 参数
    """
    username = wtforms.StringField(
        label="Username",
        render_kw={
            "class": "form-control",
            "placeholder": "Please enter your username."
        },
        validators=[
            validators.DataRequired("The username cannot be empty !")
        ]
    )

    password = wtforms.PasswordField(
        label="Password",
        render_kw={
            "class": "form-control",
            "placeholder": "Please enter your password."
        },
        validators=[
            validators.DataRequired("The password cannot be empty !") 
        ]
    )
    confirm_password = wtforms.PasswordField(
        label="Comfirm Password",
        render_kw={
            "class": "form-control",
            "placeholder": "Please enter your password again."
        },
        validators=[
            validators.DataRequired("The two passwords you entered did not match !") 
        ]
    )

    submit = wtforms.SubmitField(
        label="Submit",
        render_kw={
            "class": "btn btn-primary btn-block",
        },
    )