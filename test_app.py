#-*- coding: utf-8 -*-

import pytest
from config import basedir
from app import app, db
from app.models import User, Post
import flask
from flask import url_for


@pytest.yield_fixture()
def init():
    """ Fixture for test initialisation
    """
    # App configuration overide
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SERVER_NAME'] = 'localhost'
    # DB creation
    db.create_all()
    # Context setup
    context = app.app_context()
    context.push()
    yield
    db.session.remove()
    db.drop_all()
    context.pop()

def login(user):
    return app.test_client().post('/login', data=dict(
        id=user,
        ), follow_redirects=True)



def test_index(init):
    # Assert first page without login-in
    r = app.test_client().get(url_for('index'))
    data = r.get_data()
    assert r.status_code == 200
    assert b'login' in data
    assert b'logout' not in data
    assert b'<title>Home' in data
    # Assert first page after login-in
    r = login('123')
    data = r.get_data()
    assert r.status_code == 200
    assert b'login' not in data
    assert b'logout' in data
    assert b'<title>Home' in data


def test_loginOut(init):
    # Assert login page rendering
    r = app.test_client().get(url_for('login'))
    data = r.get_data()
    assert r.status_code == 200
    assert b'<title>Sign In' in data
    assert b'Please Sign In' in data
    assert b'login' in data
    assert b'logout' not in data
    # Assert wrong login
    r = login('wrongUser')
    data = r.get_data()
    assert r.status_code == 200
    assert b'Invalid login. Please try again.' in data
    assert b'<title>Sign In' in data
    assert b'Please Sign In' in data
    assert b'login' in data
    assert b'logout' not in data
    # Assert login-in
    r = login('123')
    data = r.get_data()
    assert r.status_code == 200
    assert b'<title>Home' in data
    assert b'login' not in data
    assert b'logout' in data

    # Assert page redirection when asking if already logged
    
   # with app.test_request_context('/'):
   #     app.preprocess_request()
   #     print(flask.g.user.nickname)
    
    # r = app.test_client().get(url_for('login'))
    # data = r.get_data()
    # assert r.status_code == 200
    # assert b'<title>Home' in data
    # assert b'login' not in data
    # assert b'logout' in data
    
    # Assert logout
    r = app.test_client().get(url_for('logout'))
    data = r.get_data()
    print(data)
    assert r.status_code == 302
    assert b'You should be redirected automatically to target URL: <a href="/index">/index</a>.' in data


def test_post(init):
    r = app.test_client().post(url_for('post'), data='{"wrong": "message"}', follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'No "body" tag found'
    login('123')
    r = app.test_client().post(url_for('post'), data='{"body": "message abc"}', follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok\n'
    user = User.query.filter_by(nickname='123').first()
    posts = user.posts.all()
    assert posts[0].body == 'message abc'
    assert posts[0].timestamp is not None
    assert posts[0].logCode is None
    

