from flask import render_template, redirect, request, url_for
from app import app
from app.utils import transport, config_helper, mfs_exceptions, useful_functions
from app.utils.log_helper import logger
from app.decorators import login_required
from app.views.data import make_remote_tree, isdir

import os

@app.route('/trash', methods = ['GET', 'POST'])
@login_required
def trash():
    tree, errors = {}, {}
    trash_path = ''
    host = config_helper.moose_options['master_host']
    port = config_helper.moose_options.get('master_port', 9421)
    try:
        con = transport.Connect(host)

        if request.method == 'POST':
            return render_template('trash/trash_tree.html',
                                   post_url = '/trash/info',
                                   tree = make_remote_tree(con, request.values['full_name']))
        
        trash_path = get_trash_path(con)
        # Trash path is undefined
        if not trash_path:
            raise mfs_exceptions.MFSMountException(
                    "Couldn't get trash path from /etc/fstab and %s." % \
                    config_helper.DEFAULT_MFSTOOL_CONFIG_PATH)
            
        # Checking if mount point exists; create it otherwise
        if not con.path_exists(trash_path):
            con.remote_command("mkdir -p %s" % trash_path, 'stdout')

        # Cheking if data_path already mounted
        # 0 - is mounted, 1 - is NOT mounted
        mount_code = con.remote_command('/bin/mountpoint %s' % trash_path, 'code')
        if mount_code:
            stdout, stderr = con.remote_command('/usr/bin/mfsmount %s -H mfsmaster -o mfsmeta' % trash_path, 'std')
            # Here are weird errors which I don't understand, but path is mounted successfully
            if stderr:
                raise mfs_exceptions.MFSMountException(
                            "Couldn't mount trash path %s.\n" % trash_path + \
                            "Got the following error: %s" % stderr)

    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = useful_functions.nl2br(str(e))
    
    except mfs_exceptions.MFSMountException as e:
        errors['mount'] = (useful_functions.nl2br(str(e)), )
    
    else:
        trash_path = os.path.join(trash_path, 'trash')
        tree = make_remote_tree(con, trash_path)

    
    return render_template('trash/trash.html',
                           post_url = '/trash/info',
                           path = trash_path,
                           errors = errors,
                           tree = tree,
                           title = 'Trash')


def get_trash_path(connection):
    """
    Tries to get trash path from /etc/fstab and then from 
    moosefs_tool.ini. Returns empty if it fails.
    """
    path = ''
    try:
        logger.info('Getting trash path from /etc/fstab.')
        f = connection.get_file('/etc/fstab', 'r')
        for line in f.readlines():
            if line.startswith('mfsmount') and 'mfsmeta' in line:
                path = line.split()[1]
                logger.info('Trash path %s was got successfully.' % path)
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
        logger.info('Getting trash path from moosefs_tool.ini.')
        path = config_helper.moose_options.get('trash_path', '')
        if path:
            logger.info('Trash path %s was got successfully.' % path)

    return path


@app.route('/trash/info', methods = ['POST'])
def trash_info():
    msg, error = '', ''
    path = request.values['full_name']
    file_path, file_name = os.path.split(path)
    paths = file_name.split('|')[1:]
    action = request.values['action']
    if action == 'restore':
        host = config_helper.moose_options['master_host']
        try:
            con = transport.Connect(host)
            trash_path = get_trash_path(con)
            command = 'mv {0}/trash/*{1}* {0}/trash/undel'.format(trash_path, file_name)
            ret_code = con.remote_command(command, 'code')
        except Exception as e:
            error = str(e)
        else:
            if ret_code != 0:
                error = 'Error while running remote command %s' % command
            else:
                return ''
    return render_template('trash/trash_info.html',
                           error = error,
                           msg = msg,
                           post_url = '/trash/info',
                           paths = paths,
                           path = path)
