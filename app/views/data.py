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
    tree, errors = {}, {}
    data_path = ''
    host = config_helper.moose_options['master_host']

    try:
        con = transport.Connect(host)
        
        if request.method == 'POST':
            return render_template('data/files_tree.html',
                                   post_url = "/data/info",
                                   tree = make_remote_tree(con, request.values['full_name']))

        data_path = get_data_path(con)
        # Data path is undefined
        if not data_path:
            raise mfs_exceptions.MFSMountException(
                    "Couldn't get data path from /etc/fstab and %s." % \
                    config_helper.DEFAULT_MFSTOOL_CONFIG_PATH)
        
        # Cheking if mount point exists and create it otherwise
        if not con.path_exists(data_path):
            stdout, stderr = con.remote_command("mkdir -p %s" % data_path, 'std')
            if stderr:
                raise mfs_exceptions.MFSMountException(
                            "Couldn't create mount point %s.\n" % data_path + \
                            "Got the following error: %s" % stderr)
                
        # Cheking if data_path already mounted
        # 0 - is mounted, 1 - is NOT mounted
        mount_code = con.remote_command('/bin/mountpoint %s' % data_path, 'code')
        if mount_code:
            ret_code = con.remote_command('/usr/bin/mfsmount %s' % data_path, 'code')
            # 0 - correct command; not 0 - command with errors
            if ret_code:
                raise mfs_exceptions.MFSMountException(
                            "Couldn't mount data path %s.\n" % data_path + \
                            "Got the following return code: %s" % ret_code)

    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = (useful_functions.nl2br(str(e)), )
    
    except mfs_exceptions.MFSMountException as e:
        errors['mount'] = (useful_functions.nl2br(str(e)), )
    
    else:
        tree = make_remote_tree(con, data_path)
    
    return render_template('data/data.html',
                           post_url = "/data/info",
                           tree = tree,
                           path = data_path,
                           errors = errors,
                           title = 'Data')


@app.route('/data/info', methods = ['POST'])
def get_file_info():
    host = config_helper.moose_options['master_host']
    con = transport.Connect(host)
    # possible action's types: mfsdirinfo, mfsfileinfo, mfscheckfile
    action = str(request.values['action'])
    data, err = con.remote_command('%s %s' % (action, request.values['full_name']), 'std')
    return render_template('data/getinfo.html',
                           post_url = "/data/info",
                           full_name = request.values['full_name'],
                           is_dir = request.values['is_dir'],
                           action = action,
                           data = data
                           )

def get_data_path(connection):
    """
    Tries to get data path from /etc/fstab and then from 
    moosefs_tool.ini. Returns empty if it fails.
    """
    path = ''
    try:
        logger.info('Getting data path from /etc/fstab.')
        f = connection.get_file('/etc/fstab', 'r')
        for line in f.readlines():
            if line.startswith('mfsmount') and 'mfsmeta' not in line:
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
        logger.info('Getting data path from %s.' % \
                    config_helper.DEFAULT_MFSTOOL_CONFIG_PATH)
        path = config_helper.moose_options.get('data_path', '')
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