from flask import render_template, redirect, request, url_for
from app import app
from app.forms import BackupForm
from app.decorators import login_required
from app.utils import mfs_exceptions, transport, config_helper, moose_lib, \
                      backup_helper, useful_functions
from app.utils.log_helper import logger

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
DEFAULT_CONFIGS_PATH = '/etc/mfs'
DEFAULT_MFSMASTER_PORT = 9421

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    configs_info, meta_info, mfsmaster_info, backup_form = (None,)*4
    errors = []
    host = config_helper.moose_options.get('master_host', '')
    try:
        con = transport.Connect(host)
    except mfs_exceptions.MooseConnectionFailed as e:
        errors.append(useful_functions.nl2br(str(e)))
    else:
        backup_form = BackupForm(request.form)
        
        configs_info = get_configs_info(con)
        configs_path = configs_info['configs_path']
        mfsmaster_info = get_mfsmaster_info(con, host, configs_path)
        meta_path = mfsmaster_info['meta_path']
        port = config_helper.moose_options.get('master_port',
                                               mfsmaster_info['port'])
        meta_info = get_meta_info(meta_path, con, configs_path)
        
        if request.method == 'POST':
            if 'action' in request.values: # save or edit config
                action = request.values['action']
                return globals()[action + '_config'](con, configs_path,
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
            mfsmaster_info.iteritems = mfsmaster_info.items
    return render_template('master/master.html',
                           configs_info = configs_info,
                           meta_info = meta_info,
                           mfsmaster_info = mfsmaster_info,
                           backup_form = backup_form,
                           errors = errors,
                           title = 'Master')

def get_value_by_key(key, content):
    """
    Parse content and retruns value which corresponds 
    to given key.
    """
    line = "".join([l for l in content if key in l])
    try:
        s = re.search(r'^( |[^#])?%s ?= ?(?P<value>[A-Za-z0-9\/]+)' % key, line)
        value = s.group('value')
        return value
    except AttributeError as e:
        return None

def get_mfsmaster_info(connection, host, configs_path):
    """
    returns some of mfsmaster options in a dictionary
    or gives default values, asigned in this module
    """
    errors = []
    mfsmaster_cfg_path = os.path.join(configs_path, CONFIGS[0])
    meta_path, port, version = '', '', ''
    
    try:
        mfsmaster_cfg = connection.get_file(mfsmaster_cfg_path, 'r')
        lines = mfsmaster_cfg.readlines()
        
        meta_path = get_value_by_key('DATA_PATH', lines)
        if not meta_path:
            meta_path = DEFAULT_META_PATH
        
        port = get_value_by_key('MATOCL_LISTEN_PORT', lines)
        if not port:
            port = DEFAULT_MFSMASTER_PORT
        
        version = get_master_version(host, port)
        if not isinstance(version, tuple):
            errors.append(version)

    except mfs_exceptions.OpenRemoteFileFailed:
        error = 'Cannot find \"%s\" in %s.' % (CONFIGS[0], configs_path)
        logger.error(mfs_exceptions.MetafilesException(error))
        errors.append(error)
    else:
        mfsmaster_cfg.close()
    return {
            'meta_path' : meta_path,
            'port' : port,
            'version' : version,
            'host' : host,
            'errors' : errors
            }


def get_configs_info(connection, files_list=CONFIGS.values()):
    """
    Tries to get configs_path from moosefs_tool.ini.
    Checks files from files_list in configs_path on remote host.
    Adds config's errors if they are.
    """
    errors = []
    configs_path = ''
    configs = []
    try:
        configs_path = config_helper.moose_options.get('configs_path', DEFAULT_CONFIGS_PATH)
    except Exception as e:
        msg = 'Cannot get \"configs_path\".<br/>%s' % str(e)
        logger.error(mfs_exceptions.ConfigsException(msg))
        errors.append(msg)
    else:
        for file in files_list:
            full_path = os.path.join(configs_path, file)
            
            if connection.path_exists(full_path):
                f = connection.get_file(full_path, 'r')
                configs.append(file)
                f.close()
            
            else:
                msg = '\"%s\" is missing in %s.' % (file, configs_path)
                logger.error(mfs_exceptions.ConfigsException(msg))
                errors.append(msg)
        
        if not configs:
            msg = 'You have no configs in %s.<br/>' % configs_path
            logger.error(mfs_exceptions.ConfigsException(msg))
            errors.append(''.join([msg,
                    'Please check \"configs_path\" option in moosefs_tool.ini']))
    
    return {
            'configs_path' : configs_path,
            'configs' : configs,
            'errors' : errors,
            }


def get_meta_info(meta_path, connection, configs_path):
    """
    Gets DATA_PATH option from configs_path/mfsmaster.cfg file and tries 
    to get information about metafiles in DATA_PATH. 
    Adds errors if mfsmaster.cfg is missing or
    DATA_PATH is not readable or not exists.
    """
    errors = []
    metafiles = []
    
    if connection.path_exists(meta_path):
        metafiles = connection.get_files_info(meta_path)
    else:
        msg = 'Metafiles path % s does not exist.' % meta_path
        logger.error(mfs_exceptions.MetafilesException(msg))
        errors.append(''.join([msg,
                    '<br/>Change DATA_PATH option in mfsmaster.cfg.']))
    
    return {
            'metafiles' : metafiles,
            'errors' : errors,
            }


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


def get_master_version(host, port):
    try:
        mfs = moose_lib.MooseFS(masterhost=host,
                                masterport=int(port))
        version = mfs.masterversion
    except Exception as e:
        error = 'Failed to connect to %s:%s.<br/>%s' % (host, port, e)
        logger.error(error)
        return mfs_exceptions.MooseConnectionFailed(error)
    else:
        return version