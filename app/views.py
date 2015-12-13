#-*- coding: utf-8 -*-

from datetime import datetime
from os import urandom
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.security import Security, SQLAlchemyUserDatastore, login_required, current_user, auth_token_required
from app import app, db
from .forms import LoginForm
from .models import User, Post




# Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)



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
    
        Body : Text to be stored/push
        
        :return: 'ok' if success, an error otherwise
    """
    data = request.get_json(force=True, silent=False)
    print(data)
    body = data.get('body', None)
    if body is None:
        return 'No "body" tag found'  
    user = User.query.filter_by(nickname='123').first()
    post = Post(body=body, timestamp=datetime.utcnow(), userId=user.id)
    db.session.add(post)
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
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index')) 
    posts = current_user.posts.all()
    return render_template('user.html',
                           user=user,
                           posts=posts)





@app.before_first_request
def create_user():
    #user_datastore.create_user(nickname='utest', email='utest@test.com', password='ptest')
    #db.session.commit()
    pass
    








