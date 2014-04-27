from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.utils import transport, config_helper, mfs_exceptions, useful_functions
from app.utils.log_helper import logger
from app.decorators import login_required
from stat import S_ISDIR

import os
import hashlib


@app.route('/data', methods = ['GET', 'POST'])
@login_required
def data():
    tree, path = None, None
    errors = {}
    host = config_helper.roots['master_host']
    try:
        con = transport.Connect(host)
    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = (useful_functions.nl2br(str(e)), )
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
    host = config_helper.roots['master_host']
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
        path = config_helper.roots.get('data_path', '')
        if path:
            logger.info('Data path %s was got successfully.' % path)
    return path


def make_remote_tree(connection, path):
    tree = []
    try: 
        lst = connection.remote.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            try:
                children = len(connection.remote.listdir(fn))
            except OSError:
                children = []
            except Exception as e:
                children = []
            d = dict(is_dir = False,
                     name = name,
                     full_name = fn,
                     id = _set_id(fn),
                     children = children)
            if isdir(connection, fn):
                d['is_dir'] = True
            tree.append(d)
    return tree


def isdir(connection, path):
    try:
        return S_ISDIR(connection.remote.stat(path).st_mode)
    except IOError:
        #Path does not exist, so by definition not a directory
        return False


def _set_id(full_name):
    return hashlib.md5(full_name).hexdigest()