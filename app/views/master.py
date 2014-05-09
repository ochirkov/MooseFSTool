from flask import render_template, redirect, request, url_for
from app import app
from app.forms import BackupForm
from app.decorators import login_required
from app.utils import mfs_exceptions, transport, config_helper, moose_lib, \
                      backup_helper, useful_functions
from app.utils.log_helper import logger
from collections import OrderedDict

import os
import re
import sys
PY3 = sys.version_info >= (3, 0)


CONFIGS = {
       0 : "mfsmaster.cfg",
       1 : "mfsexports.cfg", 
       2 : "mfstopology.cfg"
    }

DEFAULT_META_PATH = '/var/lib/mfs'

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    config_path, configs, meta_path, metafiles, master_info, backup_form = (None,)*6
    errors = {}
    host = config_helper.roots['master_host']
    port = config_helper.roots.get('master_port', 9421)
    try:
        con = transport.Connect(host)
    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = (useful_functions.nl2br(str(e)), )
    else:
        backup_form = BackupForm(request.form)
        
        master_info, errors          = get_master_info(host, port, errors)
        config_path, configs, errors = get_config_info(con, errors)
        meta_path, metafiles, errors = get_meta_info(con, errors, config_path)
    
        if request.method == 'POST':
            if 'action' in request.values: # save or edit config
                action = request.values['action']
                return globals()[action + '_config'](con, config_path,
                                                     request.values['config_name'])
            
            else:                          # backup request
                path = backup_form.path.data
                if con.path_exists(path):
                    err = backup_helper.create_targz(path, meta_path, suffix='mfs_metadata')
                    if err:
                        backup_form.path.errors += ('Exception occured while creating backup:<br>%s.' % err,)
                    else:
                        return redirect(url_for('master'))
                else:
                    backup_form.path.errors += ('This path does not exist.',)
        if PY3:
            master_info.iteritems = master_info.items
    return render_template('master/master.html',
                           config_path = config_path,
                           configs = configs,
                           meta_path = meta_path,
                           metafiles = metafiles,
                           master_info = master_info,
                           backup_form = backup_form,
                           errors = errors,
                           title = 'Master')


def get_config_info(connection, errors, files_list=CONFIGS.values()):
    """
    Tries to get config_path from moosefs_tool.ini.
    Checks files from files_list in config_path on remote host.
    Adds config's errors if they are.
    """
    errors['configs'] = []
    config_path = ''
    configs = []
    try:
        config_path = config_helper.roots['config_path']
    except KeyError:
        msg = 'Cannot get \"config_path\" option from moosefs_tool.ini'
        logger.error(mfs_exceptions.ConfigsException(msg))
        errors['configs'].append(''.join([msg,
                                '<br/>Please set \"config_path\" option',
                                'and restart application.']))
    else:
        for file in files_list:
            full_path = os.path.join(config_path, file)
            
            if connection.path_exists(full_path):
                f = connection.get_file(full_path, 'r')
                configs.append(file)
                f.close()
            
            else:
                msg = '\"%s\" is missing in %s.' % (file, config_path)
                logger.error(mfs_exceptions.ConfigsException(msg))
                errors['configs'].append(msg)
        
        if not configs:
            msg = 'You have no configs in %s.<br/>' % config_path
            logger.error(mfs_exceptions.ConfigsException(msg))
            errors['configs'].append(''.join([msg,
                    'Please check \"config_path\" option in moosefs_tool.ini']))
    
    return config_path, configs, errors


def get_meta_info(connection, errors, config_path):
    """
    Gets DATA_PATH option from config_path/mfsmaster.cfg file and tries 
    to get information about metafiles in DATA_PATH. 
    Adds errors if mfsmaster.cfg is missing or
    DATA_PATH is not readable or not exists.
    """
    errors['metafiles'] = []
    meta_path = ''
    metafiles = []
    
    mfsmaster_cfg_path = os.path.join(config_path, CONFIGS[0])
    
    try:
        mfsmaster_cfg = connection.get_file(mfsmaster_cfg_path, 'r')
        line = "".join([l for l in mfsmaster_cfg.readlines() if 'DATA_PATH' in l])
        try:
            s = re.search(r'^( |[^#])?DATA_PATH ?= ?(?P<path>[\w|\/]+)', line)
            meta_path = s.group('path')
        except AttributeError:
            meta_path = DEFAULT_META_PATH

        if connection.path_exists(meta_path):
            metafiles = connection.get_files_info(meta_path)
        else:
            msg = 'Metafiles path % s does not exist.' % meta_path
            logger.error(mfs_exceptions.MetafilesException(msg))
            errors['metafiles'].append(''.join([msg,
                        '<br/>Change DATA_PATH option in mfsmaster.cfg.']))

    except mfs_exceptions.OpenRemoteFileFailed:
        msg = 'Cannot find \"%s\" in %s.' % (CONFIGS[0], config_path)
        logger.error(mfs_exceptions.MetafilesException(msg))
        errors['metafiles'].append(msg)
    
    else:
        mfsmaster_cfg.close()
    
    return meta_path, metafiles, errors


def edit_config(connection, path, config_name):
    """
    Returns template for config file editing.
    """
    filename = os.path.join(path, config_name)
    try:
        f = connection.get_file(filename, 'r')
        content = f.read()
    except Exception as e:
        logger.exception(e)
    finally:
        f.close()
    return render_template('master/edit_config.html',
                           filename = filename,
                           filecontent = content)


def save_config(connection, path, config_name):
    """
    Saves config file with new content.
    Returns empty string for valid flask response and error message otherwise.
    """
    new_content = request.values.get('content', '')
    root_passwd = request.values.get('root_passwd', '')
    if new_content:
        try:
            f = connection.get_file(os.path.join(path, config_name), 'w')
        except Exception as e:
            logger.exception(e)
            return 'Error while opening file %s.<br>%s' % (config_name, e)
        else:
            f.write(new_content)
            f.close()
            logger.info('%s was successfully saved.' % config_name)
            
    elif not new_content:
        msg = 'Attempting for writing of empty content to %s.' % config_name
        logger.error(msg)
        return msg
    else:
        return 'Invalid root password.'
                
    return ''


def get_master_info(host, port, errors):
    """
    Returns master host, port and version.
    """
    errors['master_info'] = []
    version = ''
    try:
        mfs = moose_lib.MooseFS(masterhost=host,
                                masterport=int(port))
        version = mfs.masterversion
    except Exception as e:
        errors['master_info'].append('Error while trying to connect to %s:%s<br/>%s'\
                                                             % (host, port, e))
        result = []
    else:
        result =  OrderedDict({'Host' : host,
                               'Port' : port,
                               'Version' : version})
    return result, errors
    
