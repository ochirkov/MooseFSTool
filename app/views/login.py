from flask import render_template, flash, session, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.utils.validate_creds import creds_validator

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():

        username = form.username.data
        password = form.password.data
        # check credentials
        if username == 'root':
            session['username'] = username
        flash('Login successful')
        return redirect(url_for('home'))
    else:
        flash('Invalid credentials')
    return render_template('login.html',
                            title = 'Sign In',
                            form = form)


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home', methods = ['GET', 'POST'])
def home():
    return render_template('main.html',
                           title = 'Home')