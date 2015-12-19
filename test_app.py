#-*- coding: utf-8 -*-

import pytest
from datetime import datetime
from config import basedir
from app import app, db
from app.models import User, Post
import flask
from flask import url_for
from sqlalchemy import func


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
    user = User(nickname='utest', email='utest@test.com', password='pptest', active=True)
    db.session.add(user)
    db.session.commit()
    # Context setup
    context = app.app_context()
    context.push()
    yield
    db.session.remove()
    db.drop_all()
    context.pop()

def login(email, password):
    return app.test_client().post(url_for('security.login'), data=dict(email=email, password=password)
         , follow_redirects=True)



def test_index(init):
    # Assert first page without login-in
    r = app.test_client().get(url_for('index'))
    data = r.get_data()
    assert r.status_code == 200
    assert b'login' in data
    assert b'logout' not in data
    assert b'<title>Home' in data
    # Assert first page after login-in
    r = login('utest@test.com', 'pptest')
    data = r.get_data()
    assert r.status_code == 200
    assert b'login' not in data
    assert b'logout' in data
    assert b'<title>Home' in data


def test_loginOut(init):
    # Assert login page rendering
    r = app.test_client().get(url_for('security.login'))
    data = r.get_data()
    assert r.status_code == 200
    assert b'<title>Log in' in data
    assert b'Please log in' in data
    assert b'login' in data
    assert b'logout' not in data
    # Assert wrong login
    r = login('wrongUser' , 'wrongPassword')
    data = r.get_data()
    assert r.status_code == 200
    assert b'Specified user does not exist' in data
    assert b'<title>Log in' in data
    assert b'Please log in' in data
    assert b'login' in data
    assert b'logout' not in data
    # Assert wrong password
    r = login('utest@test.com' , 'wrongPassword')
    data = r.get_data()
    assert r.status_code == 200
    assert b'Invalid password' in data
    assert b'<title>Log in' in data
    assert b'Please log in' in data
    assert b'login' in data
    assert b'logout' not in data
    # Assert login-in
    r = login('utest@test.com', 'pptest')
    data = r.get_data()
    assert r.status_code == 200
    assert b'<title>Home' in data
    assert b'login' not in data
    assert b'logout' in data


    # Assert page redirection when asking if already logged - TODO
    
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
    r = app.test_client().get(url_for('security.logout'))
    data = r.get_data()
    assert r.status_code == 302
    assert b'You should be redirected automatically to target URL: <a href="/index">/index</a>.' in data
   
    

def test_post(init):
    user = User.query.filter_by(nickname='utest').first()
    # Assert not authorised
    r = app.test_client().post(url_for('post'), data='{"wrong": "message"}', follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 401
    assert b'<h1>Unauthorized</h1>' in data
    # Assert bad request
    r = app.test_client().post(url_for('post'), data = '',
                                    headers={'authentication_token': user.get_auth_token()},
                                    follow_redirects=True)
    assert r.status_code == 400
    # Assert no body tag found
    r = app.test_client().post(url_for('post'), data = '{}',
                                    headers={'authentication_token': user.get_auth_token()},
                                    follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'No "body" tag found'
    # Assert post
    r = app.test_client().post(url_for('post'), data='{"body": "message abc", "badge": "W"}',
                                    headers={'authentication_token': user.get_auth_token()},
                                    follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    posts = user.posts.all()
    assert posts[0].body == 'message abc'
    assert posts[0].timestamp is not None
    assert posts[0].badge is 'W' # TODO - Test badge is None
    # Assert post without badge
    with pytest.raises(IndexError):
        assert posts[1] is None
    r = app.test_client().post(url_for('post'), data='{"body": "message abcd"}',
                                    headers={'authentication_token': user.get_auth_token()},
                                    follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    posts = user.posts.all()
    assert posts[1].body == 'message abcd'
    assert posts[1].timestamp is not None
    assert posts[1].badge is None
    # Asserr only two posts
    with pytest.raises(IndexError):
        assert posts[2] is None
    

def test_register(init):
    # Assert missing all
    r = app.test_client().post('/register', data={
        'password': '',
        'nickname': '',
        'password_confirm': '',
        'email': ''
    }, follow_redirects=True)
    data = r.get_data()
    assert b'This field is required.' in data
    assert b'Email not provided' in data
    assert b'Password not provided' in data
    assert b'<title>Register' in data
    # Assert nickname already registered and no registration
    r = app.test_client().post('/register', data={
        'password': 'azerty',
        'nickname': 'utest',
        'password_confirm': 'azerty',
        'email': 'user2@user.com'
    }, follow_redirects=True)
    data = r.get_data()
    assert b'Nickname already exists' in data
    assert db.session.query(func.count(User.id)).scalar() == 1
    # Assert registration succeded
    r = app.test_client().post('/register', data={
        'password': 'azerty',
        'nickname': 'user',
        'password_confirm': 'azerty',
        'email': 'user2@user.com'
    }, follow_redirects=True)
    data = r.get_data()
    assert b'<title>Home' in data
    assert db.session.query(func.count(User.id)).scalar() == 2    
        
def test_misc():
    # User repr
    user = User(nickname='utest', email='utest@test.com', password='pptest', active=True)
    assert str(user) == "<User 'utest'>"
    # Post repr
    post = Post(body='message abc', timestamp=datetime.utcnow(), userId=1)
    assert str(post) == "<Post 'message abc'>"
    
    

