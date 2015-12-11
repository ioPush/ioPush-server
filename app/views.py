from datetime import datetime
from os import urandom
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import LoginForm
from .models import User, Post

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
                           title='Home',
                           user=user)
                           
                           
@app.route('/login', methods=['GET', 'POST'])
def login():
    print('G.user :', g.user)
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return login(form.id.data)
    return render_template('login.html', 
                           title='Sign In',
                           form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
    
@app.route('/api/post', methods=['POST'])
def post():
    data = request.get_json(force=True, silent=False)
    print(data)
    body = data.get('body', None)
    if body is None:
        return 'No "body" tag found'  
    user = User.query.filter_by(nickname='123').first()
    post = Post(body=body, timestamp=datetime.utcnow(), userId=user.id)
    db.session.add(post)
    db.session.commit()
    return 'ok\n'


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    if nickname != g.user.nickname:
        flash('Wrong user')
        return redirect(url_for('index'))
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index')) 
    posts = g.user.posts.all()
    return render_template('user.html',
                           user=user,
                           posts=posts)


@lm.user_loader
def loadUser(id):
    return User.query.get(int(id))


def login(formData):
    if (formData != "test123") and (formData != "123"):
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=formData+"@test.com").first()
    if user is None:
        nickname = formData
        user = User(nickname=nickname, email=formData+"@test.com", apiKey=urandom(20)) 
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.before_request
def before_request():
    g.user = current_user
