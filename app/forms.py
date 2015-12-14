#-*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from flask_security.forms import RegisterForm


class ExtendedRegisterForm(RegisterForm):
    #TODO - Check if nickname is unique
    nickname = StringField('Nickname', [DataRequired()])
