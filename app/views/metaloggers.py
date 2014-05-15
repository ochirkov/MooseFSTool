from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.config_helper import moose_options, mfs_exceptions, DEFAULT_MFSMASTER_PORT
from app.utils.moose_lib import MooseFS

@app.route('/metaloggers', methods = ['GET', 'POST'])
@login_required
def metaloggers():
    host = moose_options.get('master_host', '')
    port = moose_options.get('master_port', DEFAULT_MFSMASTER_PORT)
    metaloggers, errors = [], []
    try:
        mfs = MooseFS(masterhost=host,
                      masterport=int(port))
    except mfs_exceptions.MooseConnectionFailed as e:
        errors.append("Failed to connect to mfsmaster.\n%s" % e)
    except Exception as e:
        errors.append('Failed to connect to %s:%s.\n%s' % (host, port, e))
    # available keys: host, ip
    else:
        try:
            metaloggers = mfs.mfs_backup_servers()
        except Exception as e:
            errors.append('Error while getting metaloggers %s' % e)
    return render_template('backupservers-info.html',
                           errors = errors,
                           servers = metaloggers,
                           title = 'Metaloggers')