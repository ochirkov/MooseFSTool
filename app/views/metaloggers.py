from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.common_functions import mfs_object


@app.route('/metaloggers', methods = ['GET', 'POST'])
@login_required
def metaloggers():
    mfs_obj = mfs_object()
    mfs = mfs_obj['mfs']
    errors = mfs_obj['errors']
    metaloggers = []
    if mfs:
        # available keys: host, ip
        metaloggers = mfs.mfs_backup_servers()
    return render_template('servers.html',
                           servers_table = 'metaloggers-table.html',
                           errors = errors,
                           servers = metaloggers,
                           title = 'Metaloggers')