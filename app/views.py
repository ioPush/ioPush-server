# -*- coding: utf-8 -*-

from datetime import datetime
from os import urandom
from flask import render_template, flash, redirect, session, \
        url_for, request, g, jsonify
from flask.ext.security import login_required, \
        current_user, auth_token_required, http_auth_required
from flask_security.signals import user_registered, \
        password_reset, password_changed
from sqlalchemy import asc, desc, orm
from app import app, db, gcm, security, user_datastore
from .models import User, Post, Device





@app.route('/api')
@app.route('/api/')
@app.route('/')
@app.route('/index')
def index():
    """ Return index template

        :return: Index template
    """
    return render_template("index.html",
                           title='Home',
                           user=user)


@app.route('/api/post', methods=['GET', 'POST'])
@auth_token_required
def post():
    """ API end point to post a JSON message.

        body : Text to be stored/push
        badge : Badge to display (OK : S - Info : I - Warning : W - Error : E)

        :return: 'ok' if success, an error otherwise
    """
    if request.method == 'POST':
        data = request.get_json(force=True, silent=False)
    else:
        data = request.args
    body = data.get('body', None)
    if body is None:
        return 'No "body" tag found'
    badge = data.get('badge', None)
    push = data.get('push', None)
    post = Post(body=body, timestamp=datetime.utcnow(),
                userId=current_user.id, badge=badge)
    db.session.add(post)
    db.session.commit()
    if push is not None:
        sendMessageGCM(body, current_user, push)
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
    name = data.get('name', None)
    if name is None:
        return 'No "name" tag found'
    device = Device.query.filter_by(regId=regId).first()
    if device is not None:
        return 'Device already registered'
    device = Device(service=service, regId=regId, name=name[:60], userId=current_user.id)
    db.session.add(device)
    db.session.commit()
    return 'ok'


@app.route('/api/getAuthToken', methods=['POST'])
@http_auth_required
def apiGetAuthToken():
    """ API end point to get auth token.

        :return: authentication token
    """
    data = { "nickname": current_user.nickname, "authToken": current_user.auth_token }
    return jsonify(**data)


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
    devices = current_user.devices.order_by(asc(Device.name)).all()
    authToken = current_user.auth_token
    # Split authToken in order to allow mobile device word wrapping thanks to '<wbr>'
    authTokenSplit = [authToken[i:i+1] for i in range(0, len(authToken), 1)]
    return render_template('user.html',
                           user=user,
                           posts=posts,
                           devices=devices,
                           authTokenSplit = authTokenSplit,
                           title='Profile')


@app.route('/delete/user/<string:nickname>')
@login_required
def deleteUser(nickname):
    """ Delete user account

        :return: Redirection to index page
    """
    # TODO - Delete associated posts
    if nickname != current_user.nickname:
        flash('Wrong user')
        return redirect(url_for('index'))
    user = User.query.filter_by(nickname=nickname).first()
    user_datastore.delete_user(user)
    user_datastore.commit()
    return redirect(url_for('index'))


@app.route('/delete/post/<int:postId>', methods=['POST'])
@login_required
def deletePost(postId):
    """ Delete user post

        :return: 'ok' if success, 'nok' otherwise
    """
    post = current_user.posts.filter_by(id=postId).first()
    try:
        db.session.delete(post)
        db.session.commit()
    except orm.exc.UnmappedInstanceError:
        return 'nok'
    return 'ok'

@app.route('/delete/device/<int:deviceId>')
@login_required
def deleteDevice(deviceId):
    """ Delete selected device

        :return: Redirection to user page
    """
    device = current_user.devices.filter_by(id=deviceId).first()
    try:
        db.session.delete(device)
        db.session.commit()
        flash('Device deleted')
    except orm.exc.UnmappedInstanceError:
        flash('Error deleting device')
    finally:
        return redirect(url_for('user', nickname=current_user.nickname))


@app.route('/rename/device', methods=['POST'])
@login_required
def renameDevice():
    """ Rename selected device)
    
        :return: Redirection to user page
    """
    newName = request.form.get('newName', None)
    deviceId = request.form.get('deviceId', None)
    if newName is None:
        flash('No new name provided')
        return redirect(url_for('user', nickname=current_user.nickname))
    device = current_user.devices.filter_by(id=deviceId).first()
    if device is None:
        flash('Error renaming device')
    else:
        device.name = newName[:60]
        db.session.commit()
        flash('Device "' + device.name + '" renamed')
    return redirect(url_for('user', nickname=current_user.nickname))

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


@user_registered.connect_via(app)
def on_user_registerd(app, user, confirm_token):
    """ Catches new user registered, add first post and auth_token

        parameters : Sent by flask-Security
    """
    # Add first post
    post = Post(body='First post to your logbook', timestamp=datetime.utcnow(),
                userId=user.id, badge='S')
    db.session.add(post)
    db.session.commit()
    # Store auth_token
    user.auth_token = user.get_auth_token()
    while user.auth_token.find('@') != -1:  # Avoid '@' in auth_token for emails
        user.auth_token = user.get_auth_token()
    db.session.commit()
    # Log new user
    app.logger.info('New user "%s" - Email : %s' % (user.nickname, user.email) )

#@password_reset.connect_via(app)
@password_changed.connect_via(app)
def on_password_changed(app, user):
    """ Catches password changes, update user's auth_token

        parameters : Sent by flask-Security
    """
    user.auth_token = user.get_auth_token()
    while user.auth_token.find('@') != -1:  # Avoid '@' in auth_token for emails
        user.auth_token = user.get_auth_token()
    db.session.commit()

def sendMessageGCM(message, user, deviceName):
    """Send the push message to a user or all users if 'user' is not passed
    
    :param message: Message to send
    :param user: User to send, None if the message is for all
    """
    if ((deviceName.lower() == 'true') or (deviceName.lower() =='all')):
        devices = user.devices.all()
    else:
        devices = user.devices.filter_by(name=deviceName)

    if devices:
        data = {'text': message}
        regIds = [ device.regId for device in devices if device.service == "AndroidGCM" ]
        response = gcm.json_request(registration_ids=regIds, data=data, collapse_key='toto', delay_while_idle=True)
    
        # Errors, delete the device
        if response and 'errors' in response:
            for error, regIds in response['errors'].items():
                if error in ['NotRegistered', 'InvalidRegistration']:
                    for regId in regIds:
                        Device.query.filter_by(regId=regId).delete()
                        db.session.commit()
        # Canonical answer, update the user
        if response and 'canonical' in response:
            for regId, canonicalId in response['canonical'].items():
                device = Device.query.filter_by(regId=regId).first()
                device.regId = canonicalId
                db.session.commit()
        # Successfull calls - Code left just in case...
        '''
        if response and 'success' in response:
            for regIds, successId in response['success'].items():
                print('SUCCESS for regID %s' % regIds)
        '''
