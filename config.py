#-*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# General
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# SQL ALCHEMY
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'misc/ioPush.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'misc/db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Security
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = False # TODO
SECURITY_RECOVERABLE = False # TODO
SECURITY_TRACKABLE = False
SECURITY_PASSWORDLESS = False
SECURITY_CHANGEABLE = False

SECURITY_SEND_REGISTER_EMAIL = False # TODO