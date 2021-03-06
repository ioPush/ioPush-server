# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import basedir
from gcm import GCM
from flask.ext.security import Security, SQLAlchemyUserDatastore
import os

# Application
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_object('config')

# Database
db = SQLAlchemy(app)
from .models import User
from .forms import ExtendedRegisterForm

# Emails
mail = Mail(app)

# GCM
gcm = GCM(app.config['GCM_API_KEY'], proxy=app.config.get('GCM_PROXY', None))

# Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegisterForm)

# Log to file if the application is not in debug
if not app.debug:
    if not os.path.exists('misc/log'):
        os.makedirs('misc/log')
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
                os.path.join(basedir, '../misc/log/ioPush.log'),
                'a', 1 * 1024 * 1024, 5
                )
    file_handler.setFormatter(logging.Formatter(
                      '''%(asctime)s %(levelname)s:
                         %(message)s [in %(pathname)s:%(lineno)d]
                      '''))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('**** START ****')

from app import views, models
