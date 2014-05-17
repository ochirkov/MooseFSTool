from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.common_functions import mfs_object


@app.route('/clients', methods = ['GET', 'POST'])
@login_required
def clients():
    mfs_obj = mfs_object()
    mfs = mfs_obj['mfs']
    errors = mfs_obj['errors']
    clients = []
    try:
        # available keys: host, ip, mount_point, mfsmount_root
        clients = mfs.mfs_mounts()
    except Exception as e:
        errors.append("Clients error: %s" % str(e))
    return render_template('servers.html',
                           servers_table = 'clients-table.html',
                           servers = clients,
                           errors = errors,
                           title = 'Clients')
    