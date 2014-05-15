from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.config_helper import moose_options, mfs_exceptions, DEFAULT_MFSMASTER_PORT
from app.utils.moose_lib import MooseFS


@app.route('/clients', methods = ['GET', 'POST'])
@login_required
def clients():
    host = moose_options.get('master_host', '')
    port = moose_options.get('master_port', DEFAULT_MFSMASTER_PORT)
    clients, errors = [], []
    try:
        mfs = MooseFS(masterhost=host,
                      masterport=int(port))
    except mfs_exceptions.MooseConnectionFailed as e:
        errors.append("Failed to connect to mfsmaster.\n%s" % e)
    except Exception as e:
        errors.append('Failed to connect to %s:%s.\n%s' % (host, port, e))
    # available keys: host, ip, mount_point, mfsmount_root
    else:
        clients = mfs.mfs_mounts()
    return render_template('clients-info.html',
                           servers = clients,
                           errors = errors,
                           title = 'Clients')
    