from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.decorators import login_required
from app.utils.common_functions import mfs_object


@app.route('/chunkservers', methods = ['GET', 'POST'])
@login_required
def chunkservers():
    mfs_obj = mfs_object()
    mfs = mfs_obj['mfs']
    errors = mfs_obj['errors']
    chunkservers = []
    try:
        # available keys: host, ip
        chunkservers = mfs.mfs_servers()
    except Exception as e:
        errors.append("Chunkservers error: %s" % str(e))
    return render_template('servers.html',
                           servers_table = 'chunkservers-table.html',
                           servers = chunkservers,
                           errors = errors,
                           title = 'Chunkservers')

