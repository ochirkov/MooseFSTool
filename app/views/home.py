from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.forms import LoginForm
from app.decorators import login_required
from app.utils.common_functions import mfs_object

import os
import ast

@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))


@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    mfs_obj = mfs_object()
    mfs = mfs_obj['mfs']
    errors = mfs_obj['errors']
    clients, metaloggers, chunkservers = [], [], []
    try:
        clients = mfs.mfs_mounts()
    except Exception as e:
        errors.append("Clients error: %s" % str(e))
    try:
        metaloggers = mfs.mfs_backup_servers()
    except Exception as e:
        errors.append("Metaloggers error: %s" % str(e))
    try:
        chunkservers = mfs.mfs_servers()
    except Exception as e:
        errors.append("Chunkservers error: %s" % str(e))

    return render_template('home.html',
                           master_host = mfs.masterhost,
                           metaloggers = metaloggers,
                           chunkservers = chunkservers,
                           clients = clients,
                           errors = errors,
                           title = 'Home')

@app.template_filter('pluralize')
def pluralize(number, singular = '', plural = 's'):
    if number == 1:
        return singular
    else:
        return plural