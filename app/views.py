# -*- coding: utf-8 -*-

from datetime import datetime
from os import urandom
from flask import render_template, flash, redirect, session, \
        url_for, request, g
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
        login_required, current_user, auth_token_required
from sqlalchemy import desc
from app import app, db
from .models import User, Post, Device
from .forms import ExtendedRegisterForm


# Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore,
                    confirm_register_form=ExtendedRegisterForm)


@app.route('/')
@app.route('/index')
def index():
    """ Return index template

        :return: Index template
    """
    return render_template("index.html",
                           title='Home',
                           user=user)


@app.route('/api/post', methods=['POST'])
@auth_token_required
def post():
    """ API end point to post a JSON message.

        body : Text to be stored/push
        badge : Badge to display (OK : S - Info : I - Warning : W - Error : E)

        :return: 'ok' if success, an error otherwise
    """
    data = request.get_json(force=True, silent=False)
    body = data.get('body', None)
    if body is None:
        return 'No "body" tag found'
    badge = data.get('badge', None)
    post = Post(body=body, timestamp=datetime.utcnow(),
                userId=current_user.id, badge=badge)
    db.session.add(post)
    db.session.commit()
    return 'ok'


@app.route('/api/addDevice', methods=['POST'])
@auth_token_required
def addDevice():
    """ API end point to add a device.

        service : Service to be registered, only AndroidGCM for now
        regId : Registration Id

        :return: 'ok' if success, an error otherwise
    """
    data = request.get_json(force=True, silent=False)
    service = data.get('service', None)
    if service is None:
        return 'No "service" tag found'
    regId = data.get('regId', None)
    if regId is None:
        return 'No "regId" tag found'
    device = Device(service=service, regId=regId, userId=current_user.id)
    db.session.add(device)
    db.session.commit()
    return 'ok'


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    """ User's page

        :return: Users's page
    """
    if nickname != current_user.nickname:
        flash('Wrong user')
        return redirect(url_for('index'))
    user = User.query.filter_by(nickname=nickname).first()
    posts = current_user.posts.order_by(desc(Post.timestamp)).all()
    return render_template('user.html',
                           user=user,
                           posts=posts,
                           title='Profile')


@app.route('/user/delete/<nickname>')
@login_required
def deleteUser(nickname):
    """ Delete user account

        :return: Redirection to index page
    """
    if nickname != current_user.nickname:
        flash('Wrong user')
        return redirect(url_for('index'))
    user = User.query.filter_by(nickname=nickname).first()
    user_datastore.delete_user(user)
    user_datastore.commit()
    return redirect(url_for('index'))


@security.login_context_processor
def login_register_processor():
    return dict(title='Log in')


@security.register_context_processor
def register_register_processor():
    return dict(title='Register')


@security.change_password_context_processor
def change_password_register_processor():
    return dict(title='Change password')
    
@security.send_confirmation_context_processor
def send_confirmation_register_processor():
    return dict(title='Confirm email')
    
@security.reset_password_context_processor
def reset_password_register_processor():
    return dict(title='Reset password')
    
@security.forgot_password_context_processor
def forgot_password_context_processor():
    return dict(title='Lost password')
