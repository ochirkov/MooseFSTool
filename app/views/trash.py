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
    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = useful_functions.nl2br(str(e))
    except Exception as e:
        pass
    else:
        trash_path = get_trash_path(con)
        trash_path = os.path.join(trash_path, 'trash')
        if not isdir(con, trash_path):
            errors['mount'] = 'Path \"%s\" does not mounted.' % trash_path
        else:
            tree = make_remote_tree(con, trash_path)
            
            command = '/usr/bin/mfsmount %s -H mfsmaster -o mfsmeta' % trash_path
            resp = con.remote_command(command, 'stdout')
            if resp:
                errors['mount'] = 'Failed to mount trash folder with command \"%s\".<br/>Got following error:<br/> %s.' % (command, resp)
            
            if request.method == 'POST':
                return render_template('trash/trash_tree.html',
                                       post_url = '/trash/info',
                                       tree = make_remote_tree(con, request.values['full_name']))
    
    return render_template('trash/trash.html',
                           post_url = '/trash/info',
                           path = trash_path,
                           errors = errors,
                           tree = tree,
                           title = 'Trash')


def get_trash_path(connection):
    """
    Tries to get trash path from /etc/fstab and than from 
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
            trash_path = config_helper.moose_options['trash_path']
            con = transport.Connect(host)
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
