from flask import render_template, flash, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.utils.validate_creds import creds_validator


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
#    if request.method == 'GET':
    if request.method == 'POST':
        if creds_validator(request.form['username'], request.form['password']):

            #check user
            flash('You are already logged')
 #           return redirect(url_for('index'))
            return 'foo'
        else:
            flash('Creds invalid')
            return render_template('login.html',
                title = 'Sign In',
                form = form)
    else:
        return render_template('login.html',
            title = 'Sign In',
            form = form)

@app.route('/index', methods = ['GET'])
def index():
    return 'bla'