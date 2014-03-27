from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.log_helper import roots
from app.utils.moose_lib import MooseFS


import os

@app.route('/servers', methods = ['GET', 'POST'])
@login_required
def servers():
    host = roots['master_host']
    port = roots['master_port']
    servers = []
    try:
        mfs = MooseFS(masterhost=host,
                      masterport=port)
        servers = mfs.mfs_servers()
    except Exception as e:
        error = 'Error while trying to connect to %s:%s<br/>%s' % (host, port, e)
    return render_template('servers.html',
                           servers = servers,
                           title = 'Servers')
    