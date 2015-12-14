#-*- coding: utf-8 -*-

from app import db
from flask.ext.security import Security, UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

# User class
class User(db.Model, UserMixin):    
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id)  # python 3        
    
    # Avoid creating roles for Flash-Security
    # See https://github.com/mattupstate/flask-security/issues/188
    @hybrid_property
    def roles(self):
        return []
    @roles.setter
    def roles(self, role):
        pass
            
    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)
    logCode = db.Column(db.String(1))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return '<Post %r>' % (self.body)
