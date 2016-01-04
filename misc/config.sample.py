#-*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

# General
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# SQL ALCHEMY
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                          os.path.join(basedir, 'misc/ioPush.db') + \
                          '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'misc/db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Security
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = 'you-will-never-guess too'
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = True
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = False
SECURITY_PASSWORDLESS = False
SECURITY_CHANGEABLE = True

SECURITY_SEND_REGISTER_EMAIL = True
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
SECURITY_EMAIL_SENDER = 'no-reply@yourdomain'

SECURITY_POST_LOGIN_VIEW = 'index'
SECURITY_POST_LOGOUT_VIEW = 'index'
SECURITY_POST_REGISTER_VIEW = 'index'
SECURITY_UNAUTHORIZED_VIEW = 'index'

SECURITY_RESET_URL = '/lostPassword'

# Flask-Mail
MAIL_SERVER = 'smtp_mail_server'
MAIL_PORT = 25
MAIL_USE_SSL = False
MAIL_USE_TLS = False
MAIL_USERNAME = 'email@email.net'
MAIL_PASSWORD = 'password'
