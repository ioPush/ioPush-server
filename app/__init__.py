#-*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir
import os

# Application
app = Flask(__name__)
app.config.from_object('config')

# Database
db = SQLAlchemy(app)


from app import views, models

