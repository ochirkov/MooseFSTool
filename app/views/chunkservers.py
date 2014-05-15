from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.decorators import login_required
from app.utils.config_helper import moose_options, mfs_exceptions, DEFAULT_MFSMASTER_PORT
from app.utils.moose_lib import MooseFS


@app.route('/chunkservers', methods = ['GET', 'POST'])
@login_required
def chunkservers():
    host = moose_options.get('master_host', '')
    port = moose_options.get('master_port', DEFAULT_MFSMASTER_PORT)
    chunkservers, errors = [], []
    try:
        mfs = MooseFS(masterhost=host,
                      masterport=int(port))
    except mfs_exceptions.MooseConnectionFailed as e:
        errors.append("Failed to connect to mfsmaster.\n%s" % e)
    except Exception as e:
        errors.append('Failed to connect to %s:%s.\n%s' % (host, port, e))
    # available keys: host, ip
    else:
        chunkservers = mfs.mfs_servers()
    return render_template('chunks-info.html',
                           servers = chunkservers,
                           errors = errors,
                           title = 'Chunkservers')

