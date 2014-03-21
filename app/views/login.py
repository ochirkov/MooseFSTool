from flask import render_template, flash, session, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.utils.validate_creds import creds_validator


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():

        username = form.username.data
        password = form.password.data
        # check credentials
        if creds_validator(username, password):
            session['username'] = username
            flash('Login successful')
            return redirect(request.form['next_url'])
        else:
            form.password.errors.append("Invalid username or password")
    else:
        flash('Invalid credentials')
    return render_template('login.html',
                            title = 'Sign In',
                            form = form)


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))