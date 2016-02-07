# -*- coding: utf-8 -*-

import pytest
from datetime import datetime
from config import basedir
from app import app, db, security
from app.models import User, Post, Device
import flask
from flask import url_for
from sqlalchemy import func


# Catch emails, in order to avoid sending them
@security.send_mail_task
def send_email(msg):
  app.mail_sent = True


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
    user = User(nickname='utest',
                email='utest@test.com',
                password='pptest',
                active=True,
                confirmed_at=datetime.utcnow(),
                auth_token='d')
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
    return app.test_client().post(url_for('security.login'),
                                  data=dict(email=email, password=password),
                                  follow_redirects=True)


def test_index(init):
    # Assert first page without login-in
    r = app.test_client().get('index')
    data = r.get_data()
    assert r.status_code == 200
    assert b'login' in data
    assert b'logout' not in data
    assert b'<title>Home' in data
    # Assert it with '/' adress
    r = app.test_client().get('/')
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
    assert b'role="button">Lost password</a>' in data

    # Assert wrong login
    r = login('wrongUser', 'wrongPassword')
    data = r.get_data()
    assert r.status_code == 200
    assert b'Specified user does not exist' in data
    assert b'<title>Log in' in data
    assert b'Please log in' in data
    assert b'login' in data
    assert b'logout' not in data

    # Assert wrong password
    r = login('utest@test.com', 'wrongPassword')
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
        r = c.post(url_for('security.login'),
                   data=dict(email='utest@test.com', password='pptest'),
                   follow_redirects=True)
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
    r = app.test_client().post(
            url_for('addDevice'),
            data='{"service": "AndroidGCM", "regId": "fg79Ffg8iovwa"}',
            headers={'authentication_token': user.get_auth_token()},
            follow_redirects=True)

    # Assert not authorised
    r = app.test_client().post(url_for('post'),
                               data='{"wrong": "message"}',
                               follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 401
    assert b'<h1>Unauthorized</h1>' in data

    # Assert bad request
    r = app.test_client().post(
                url_for('post'),
                data='',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    assert r.status_code == 400

    # Assert no body tag found
    r = app.test_client().post(
                url_for('post'),
                data='{}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'No "body" tag found'

    # Assert post with POST method
    r = app.test_client().post(
                url_for('post'),
                data='{"body": "message abc", "badge": "W"}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    posts = user.posts.all()
    assert posts[0].body == 'message abc'
    assert posts[0].timestamp is not None
    assert posts[0].badge is 'W'

    # Assert post with GET method
    r = app.test_client().get(
                url_for('post'),
                query_string={'body': 'message abc 2', 'badge': 'I'},
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    posts = user.posts.all()
    assert posts[1].body == 'message abc 2'
    assert posts[1].timestamp is not None
    assert posts[1].badge is 'I'
    
    # Assert post with GET method
    r = app.test_client().get(
                url_for('post'),
                query_string={'body': 'message abc 3', 'badge': 'S', 'auth_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    posts = user.posts.all()
    assert posts[2].body == 'message abc 3'
    assert posts[2].timestamp is not None
    assert posts[2].badge is 'S'
    
    # Assert post without badge
    with pytest.raises(IndexError):
        assert posts[3] is None
    r = app.test_client().post(
                url_for('post'),
                data='{"body": "message abcd"}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    posts = user.posts.all()
    assert posts[3].body == 'message abcd'
    assert posts[3].timestamp is not None
    assert posts[3].badge is None

    # Assert only three posts
    with pytest.raises(IndexError):
        assert posts[4] is None


def test_register(init):
    # Assert missing all
    r = app.test_client().post('/register', data={
        'nickname': '',
        'password': '',
        'password_confirm': '',
        'email': ''
    }, follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
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
    assert r.status_code == 200
    assert b'Nickname already exists' in data
    assert db.session.query(func.count(User.id)).scalar() == 1
    # Register user
    r = app.test_client().post('/register', data={
        'nickname': 'utest2',
        'password': 'dfgnwxi',
        'password_confirm': 'dfgnwxi',
        'email': 'user2@user.com'
    }, follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert b'Thank you. Confirmation instructions have been sent to user2@user.com' in data
    assert db.session.query(func.count(User.id)).scalar() == 2
    # Assert first post added
    user = User.query.filter_by(nickname='utest2').first()
    posts = user.posts.all()
    assert posts[0].body == 'First post to your logbook'


def test_misc():
    # Assert User repr
    user = User(nickname='utest',
                email='utest@test.com',
                password='pptest',
                active=True)
    assert str(user) == "<User 'utest'>"

    # Assert Post repr
    post = Post(body='message abc', timestamp=datetime.utcnow(), userId=1)
    assert str(post) == "<Post 'message abc'>"
    
    # Assert Device repr
    device = Device(regId='fg79Ffg8iovwa', service='AndroidGCM', userId=1)
    assert str(device) == "<Device 'fg79Ffg8iovwa'>"


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
        r = c.post(url_for('security.login'),
                   data=dict(email='utest@test.com', password='pptest'),
                   follow_redirects=True
                   )
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
        assert b'<dt>Password' in data
        assert b'<dt>Account' in data

        # Add posts and assert their display
        post = Post(body='Post 1',
                    timestamp=datetime.utcnow(),
                    badge='I',
                    userId=1)
        db.session.add(post)
        post = Post(body='Post 2',
                    timestamp=datetime.utcnow(),
                    badge='W',
                    userId=1)
        db.session.add(post)
        post = Post(body='Post 3',
                    timestamp=datetime.utcnow(),
                    badge='S',
                    userId=1)
        db.session.add(post)
        post = Post(body='Post 4',
                    timestamp=datetime.utcnow(),
                    badge='E',
                    userId=1)
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
        user = User(nickname='utest2',
                    email='utest2@test.com',
                    password='pptest2',
                    active=True,
                    confirmed_at=datetime.utcnow())
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


def test_deleteUser(init):
    # Uses same context to stay logged-in
    with app.test_client() as c:
        # Assert login
        r = c.post(url_for('security.login'),
                   data=dict(email='utest@test.com', password='pptest'),
                   follow_redirects=True
                   )
        data = r.get_data()
        assert r.status_code == 200
        
        # Assert other user non reachable
        user = User(nickname='utest2',
                    email='utest2@test.com',
                    password='pptest2',
                    active=True,
                    confirmed_at=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        r = c.get(url_for('deleteUser', nickname='utest2'))
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
        
        # Assert user deleted
        r = c.get(url_for('deleteUser', nickname='utest'))
        data = r.get_data()
        assert r.status_code == 302
        assert b'<a href="/index">/index</a>' in data
        user = User.query.filter_by(nickname='utest').first()
        assert user is None


def test_addDevice(init):
    user = User.query.filter_by(nickname='utest').first()

    # Assert not authorised
    r = app.test_client().post(url_for('addDevice'),
                               data='{"wrong": "message"}',
                               follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 401
    assert b'<h1>Unauthorized</h1>' in data

    # Assert bad request
    r = app.test_client().post(
                url_for('addDevice'),
                data='',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    assert r.status_code == 400

    # Assert no service tag found
    r = app.test_client().post(
                url_for('addDevice'),
                data='{"regId": "fg79Ffg8iovwa"}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'No "service" tag found'

    # Assert no regId tag found
    r = app.test_client().post(
                url_for('addDevice'),
                data='{"service": "AndroidGCM"}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'No "regId" tag found'

    # Assert added device
    r = app.test_client().post(
                url_for('addDevice'),
                data='{"service": "AndroidGCM", "regId": "fg79Ffg8iovwa"}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'ok'
    devices = user.devices.all()
    assert devices[0].service == 'AndroidGCM'
    assert devices[0].regId == 'fg79Ffg8iovwa'
    
    # Assert unique regId
    r = app.test_client().post(
                url_for('addDevice'),
                data='{"service": "AndroidGCM", "regId": "fg79Ffg8iovwa"}',
                headers={'authentication_token': user.get_auth_token()},
                follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    assert data == b'Device already registered'
    devices = user.devices.all()
    assert devices[0].service == 'AndroidGCM'
    assert devices[0].regId == 'fg79Ffg8iovwa'
    with pytest.raises(IndexError):
        assert devices[1] is None


def test_auth_token(init):
    # Register user
    r = app.test_client().post('/register', data={
        'nickname': 'utest2',
        'password': 'dfgnwxi',
        'password_confirm': 'dfgnwxi',
        'email': 'user2@user.com'
    }, follow_redirects=True)
    data = r.get_data()
    assert r.status_code == 200
    # Confirm it
    user = User.query.filter_by(nickname='utest2').first()
    user.confirmed_at=datetime.utcnow()
    db.session.commit()
    
    with app.test_client() as c:
        # Login
        r = c.post(url_for('security.login'),
            data=dict(email='user2@user.com', password='dfgnwxi'),
            follow_redirects=True)
        # Get user page and store it
        r = c.get(url_for('user', nickname='utest2'))
        data = r.get_data()
        assert r.status_code == 200
        data_previous = data
        # Get user page and compare it
        r = c.get(url_for('user', nickname='utest2'))
        data = r.get_data()
        assert r.status_code == 200
        assert data_previous == data
        # Change password
        r = c.post(url_for('security.change_password'),
            data=dict(password='dfgnwxi', new_password='1256Ga', new_password_confirm='1256Ga'),
            follow_redirects=True)
        assert r.status_code == 200
        # Get user page and compare it
        r = c.get(url_for('user', nickname='utest2'))
        data = r.get_data()
        assert r.status_code == 200
        assert data_previous != data
        # Another time
        data_previous = data
        r = c.get(url_for('user', nickname='utest2'))
        data = r.get_data()
        assert r.status_code == 200
        assert data_previous == data

def test_deletePost(init):
    user = User.query.filter_by(nickname='utest').first()
    # Uses same context to stay logged-in
    with app.test_client() as c:
        # Assert login
        r = c.post(url_for('security.login'),
                   data=dict(email='utest@test.com', password='pptest'),
                   follow_redirects=True
                   )
        data = r.get_data()
        assert r.status_code == 200
 
        # Send posts
        r = app.test_client().post(
                    url_for('post'),
                    data='{"body": "message 1", "badge": "W"}',
                    headers={'authentication_token': user.get_auth_token()},
                    follow_redirects=True)
        data = r.get_data()
        assert r.status_code == 200
        r = app.test_client().post(
                    url_for('post'),
                    data='{"body": "message 2", "badge": "S"}',
                    headers={'authentication_token': user.get_auth_token()},
                    follow_redirects=True)
        data = r.get_data()
        assert r.status_code == 200
        r = app.test_client().post(
                    url_for('post'),
                    data='{"body": "message 3", "badge": "I"}',
                    headers={'authentication_token': user.get_auth_token()},
                    follow_redirects=True)
        data = r.get_data()
        assert r.status_code == 200
        
        # Assert three posts
        posts = user.posts.all()
        assert len(posts) == 3
        
        # Delete second post
        r = c.get(url_for('deletePost', postId=2),
                   follow_redirects=True
                   )
        # Assert post deleted
        data = r.get_data()
        assert r.status_code == 200
        assert b'message 1' in data
        assert b'message 2' not in data
        assert b'message 3' in data
        assert b'Post deleted' in data
        
        # Assert error
        r = c.get(url_for('deletePost', postId=2),
                   follow_redirects=True
                   )
        data = r.get_data()
        assert r.status_code == 200
        assert b'message 1' in data
        assert b'message 2' not in data
        assert b'message 3' in data
        assert b'Error deleting post' in data
        
        # TODO - Delete post of another user
        
        