from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.forms import LoginForm
from app.decorators import login_required
from app.utils.config_helper import roots
from app.utils.moose_lib import MooseFS

import os
import ast

@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))


@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    host = roots['master_host']
    port = int(roots.get('master_port', 9421))
    chunkservers = [{'ip':'192.168.56.12' + str(i), 'name' : 'chunkserver'} for i in range(3)]
    metaloggers = [{'ip':'192.168.56.13' + str(i), 'name' : 'metalogger'} for i in range(10)]
    clients = [{'ip':'192.168.56.14' + str(i), 'name' : 'client'} for i in range(10)]
    try:
        mfs = MooseFS(masterhost=host,
                      masterport=port)
#         servers = mfs.mfs_mounts()
    except Exception as e:
        error = 'Error while trying to connect to %s:%s<br/>%s' % (host, port, e)
    return render_template('home.html',
                           master_host = host,
                           metaloggers = metaloggers,
                           chunkservers = chunkservers,
                           clients = clients,
                           title = 'Home')