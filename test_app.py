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
    user = User(nickname='utest', email='utest@test.com', password='pptest', active=True, confirmed_at=datetime.utcnow())
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

    # Assert page redirection when asking if already logged
    # Uses same context to stay logged-in
    with app.test_client() as c:
        r = c.post(url_for('security.login'), data=dict(email='utest@test.com', password='pptest')
         , follow_redirects=True)
        data = r.get_data()
        assert r.status_code == 200
        assert b'<title>Home' in data
        assert b'login' not in data
        assert b'logout' in data
        r = c.get(url_for('security.login'))
        data = r.get_data()
        data = r.get_data()
        assert r.status_code == 302
        assert b'<h1>Redirecting...</h1>' in data
        assert b'<a href="/index">/index</a>' in data
    
    # Assert logout
    r = app.test_client().get(url_for('security.logout'))
    data = r.get_data()
    assert r.status_code == 302
    assert b'You should be redirected automatically to target URL: <a href="/index">/index</a>.' in data
    # Assert logged out
    r = app.test_client().get(url_for('index'))
    data = r.get_data()
    assert r.status_code == 200
    assert b'login' in data
    assert b'logout' not in data
    assert b'<title>Home' in data
   
    

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
    
    # Assert only two posts
    with pytest.raises(IndexError):
        assert posts[2] is None
    

def test_register(init):
    # Assert missing all
    r = app.test_client().post('/register', data={
        'nickname': '',
        'password': '',
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
        'nickname': 'utest',
        'password': 'azerty',
        'password_confirm': 'azerty',
        'email': 'user2@user.com'
    }, follow_redirects=True)
    data = r.get_data()
    assert b'Nickname already exists' in data
    assert db.session.query(func.count(User.id)).scalar() == 1
    # Overide email sending - TODO
    #@app.security.send_mail_task
    #def send_email(msg):
    #    app.mail_sent = True
        
def test_misc():
    # Assert User repr
    user = User(nickname='utest', email='utest@test.com', password='pptest', active=True)
    assert str(user) == "<User 'utest'>"
    
    # Assert Post repr
    post = Post(body='message abc', timestamp=datetime.utcnow(), userId=1)
    assert str(post) == "<Post 'message abc'>"
    
    
def test_user(init):
    # Uses same context to stay logged-in
    with app.test_client() as c:
    
        # Get user page without login
        r = c.get(url_for('user', nickname='test'))
        data = r.get_data()
        assert r.status_code == 302
        assert b'<title>Redirecting...</title>' in data
        assert b'<a href="/login?next=%2Fuser%2Ftest">' in data
        
        # Assert user page access after login
        r = c.post(url_for('security.login'), data=dict(email='utest@test.com', password='pptest')
         , follow_redirects=True)
        data = r.get_data()
        assert r.status_code == 200
        assert b'<title>Home' in data
        assert b'login' not in data
        assert b'logout' in data
        r = c.get(url_for('user', nickname='utest'))
        data = r.get_data()
        assert r.status_code == 200
        assert b'<title>Profile' in data
        assert b'login' not in data
        assert b'logout' in data
        assert b'<dt>Auth token</dt>' in data
        
        # Add posts and assert their display
        post = Post(body='Post 1', timestamp=datetime.utcnow(), badge='I', userId=1)
        db.session.add(post)
        post = Post(body='Post 2', timestamp=datetime.utcnow(), badge='W', userId=1)
        db.session.add(post)
        post = Post(body='Post 3', timestamp=datetime.utcnow(), badge='S', userId=1)
        db.session.add(post)
        post = Post(body='Post 4', timestamp=datetime.utcnow(), badge='E', userId=1)
        db.session.add(post)
        db.session.commit()
        r = c.get(url_for('user', nickname='utest'))
        data = r.get_data()
        assert b'Post 1' in data
        assert '<span class="pull-right label label-info">Info</span>'
        assert b'Post 2' in data
        assert '<span class="pull-right label label-info">Warning</span>'
        assert b'Post 3' in data
        assert '<span class="pull-right label label-info">OK</span>'
        assert b'Post 3' in data
        assert '<span class="pull-right label label-info">Error</span>'
        
        # Assert other user non reachable
        user = User(nickname='utest2', email='utest2@test.com', password='pptest2', active=True, confirmed_at=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        r = c.get(url_for('user', nickname='utest2'))
        data = r.get_data()
        assert r.status_code == 302
        assert b'<h1>Redirecting...</h1>' in data
        assert b'<a href="/index">/index</a>' in data
        
        # Assert flashed messsage
        r = c.get(url_for('index'))
        data = r.get_data()
        assert r.status_code == 200
        assert b'Wrong user' in data
        assert b'<div class="alert alert-info">' in data
        assert b'<button type="button" class="close" data-dismiss="alert">&times;</button>' in data
        
        
        
        
