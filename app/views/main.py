from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.forms import LoginForm
from app.decorators import login_required

import os
import ast

@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))


@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    return render_template('home.html',
                           title = 'Home')