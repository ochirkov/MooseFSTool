from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.utils import transport
from app.utils.config_helper import roots
from app.utils.log_helper import logger
from app.utils import mfs_exceptions
from app.decorators import login_required
from app.views.trash import make_remote_tree
from app.utils.mfs_exceptions import MooseConnectionFailed
from app.utils.useful_functions import nl2br


import os
import hashlib


@app.route('/data', methods = ['GET', 'POST'])
@login_required
def data():
    tree, path = None, None
    errors = {}
    host = roots['master_host']
    try:
        con = transport.Connect(host)
    except MooseConnectionFailed as e:
        errors['connection'] = (nl2br(str(e)), )
    else:
        path = get_data_path(con)
        tree= {}
        if not path:
            errors['data_path'] = 'Cannot get data path from /etc/fstab and moosefs_tool.ini.'
        else:
            command = 'mfsmount %s' % path
            resp = con.remote_command(command, 'stdout')
            tree = make_remote_tree(con, path)
            
            if request.method == 'POST':
                return render_template('data/files_items.html',
                                       tree = make_remote_tree(con, request.values['full_name']))
    
    return render_template('data/data.html',
                           tree = tree,
                           path = path,
                           errors = errors,
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
        return render_template('data/getinfo.html',
                               full_name = request.values['full_name'],
                               is_dir = request.values['is_dir'],
                               action = action,
                               data = data
                               )

def get_data_path(connection):
    """
    Tries to get data path from /etc/fstab and than from 
    moosefs_tool.ini. Returns empty if it fails.
    """
    path = ''
    try:
        logger.info('Getting data path from /etc/fstab.')
        f = connection.get_file('/etc/fstab', 'r')
        for line in f.readlines():
            if 'fuse' in line and 'mfsmount' in line:
                path = line.split()[1]
                logger.info('Data path %s was got successfully.' % path)
    except IOError:
        logger.exception(mfs_exceptions.DataPathGettingFailed(
                            'Cannot read /etc/fstab file.'))
    except IndexError:
        logger.exception(mfs_exceptions.DataPathGettingFailed(
                            'Cannot parse /etc/fstab.'))
    except Exception as e:
        logger.exception(mfs_exceptions.DataPathGettingFailed(
                            'Unresolved exception:\n%s' % e))
    if not path:
        logger.info('Getting data path from moosefs_tool.ini.')
        path = roots.get('data_path', '')
        if path:
            logger.info('Data path %s was got successfully.' % path)
    return path