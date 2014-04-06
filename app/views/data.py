from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.utils import transport
from app.utils.config_helper import roots
from app.decorators import login_required
from app.views.trash import make_remote_tree

import os
import hashlib


@app.route('/data', methods = ['GET', 'POST'])
@login_required
def data():
    host = roots['master_host']
    con = transport.Connect(host)
    path = '/mnt/mfs'
    command = 'mfsmount %s' % path
    resp = con.remote_command(command, 'stdout')
    tree = make_remote_tree(con, path)
    
    if request.method == 'POST':
        return render_template('files_items.html',
                               tree = make_remote_tree(con, request.values['full_name']))
    
    return render_template('data.html',
                           tree = tree,
                           path = path,
                           title = 'Data')


@app.route('/data/info', methods = ['POST'])
def get_file_info():
    host = roots['master_host']
    con = transport.Connect(host)
    if request.method == "POST":
        action = request.values['action']
        data = ''
        if action == 'mfsfileinfo':
            data = con.remote_command('mfsfileinfo %s' % request.values['full_name'], 'stdout')
        elif action == 'mfscheckfile':
            data = con.remote_command('mfscheckfile %s' % request.values['full_name'], 'stdout')
        elif action == 'mfsdirinfo':
            data = con.remote_command('mfsdirinfo %s' % request.values['full_name'], 'stdout')
        return render_template('getinfo.html',
                               full_name = request.values['full_name'],
                               is_dir = request.values['is_dir'],
                               action = action,
                               data = data
                               )