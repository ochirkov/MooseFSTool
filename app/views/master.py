from flask import render_template, redirect, request, url_for
from app import app
from app.forms import BackupForm
from app.decorators import login_required
from app.utils import transport
from app.utils.config_helper import roots
from app.utils.backup_helper import create_targz
from app.utils.log_helper import logger
from app.utils.moose_lib import MooseFS
from collections import OrderedDict

import os
import re


CONFIGS = {
       0 : "mfsmaster.cfg",
       1 : "mfsexports.cfg", 
       2 : "mfstopology.cfg"
    } 


@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    errors = {}
    host = roots['master_host']
    port = roots.get('master_port', 9421)
    con = transport.Connect(host)
    backup_form = BackupForm(request.form)
    
    master_info, errors               = get_master_info(host, port, errors)
    configs_path, configs, errors     = get_configinfo(con, errors)
    metafiles_path, metafiles, errors = get_metainfo(con, errors, configs_path)

    if request.method == 'POST':
        if 'action' in request.values:
            # save or edit config
            action = request.values['action']
            return globals()[action + '_config'](con, configs_path,
                                                 request.values['config_name'])
        else:
            # backup request
            path = backup_form.path.data
            if con.path_exists(path):
                create_targz(path, metafiles_path, suffix='mfs_metadata')
                return redirect(url_for('master'))
            else:
                backup_form.path.errors += ('This path does not exist.',)

    return render_template('master.html',
                           configs_path = configs_path,
                           configs = configs,
                           metafiles_path = metafiles_path,
                           metafiles = metafiles,
                           master_info = master_info,
                           backup_form = backup_form,
                           errors = errors,
                           title = 'Master')


def get_configinfo(connection, errors, files_list=CONFIGS.values()):
    """
    Tries to get configs_path from moosefs_tool.ini.
    Checks files from files_list in configs_path on remote host.
    Adds configs errors if they are.
    """
    errors['configs'] = []
    configs_path = ''
    configs = []
    try:
        configs_path = roots['configs']
    except KeyError:
        errors['configs'].append(''.join([
                                'Cannot find mfs config files.<br/>',
                                'Please set \"configs\" option in moosefs_tool.ini',
                                'and restart application.']))
    else:
        for file in files_list:
            try:
                f = connection.get_file(os.path.join(configs_path, file), 'r')
            except:
                errors['configs'].append('\"%s\" is missing in %s.' % (file, configs_path))
            else:
                configs.append(file)
            finally:
                f.close()
        
        if not configs:
            errors['configs'].append(''.join([
                            'You have no configs in %s.<br/>' % configs_path,
                            'Please check \"configs\" option in moosefs_tool.ini']))
    
    return configs_path, configs, errors


def get_metainfo(connection, errors, configs_path):
    """
    Gets DATA_PATH option from configs_path/mfsmaster.cfg file and tries 
    to get information about metafiles in DATA_PATH. 
    Adds errors if mfsmaster.cfg is missing or
    DATA_PATH is not readable or not exists.
    """
    errors['metafiles'] = []
    metafiles_path = ''
    metafiles = []
    try:
        mfsmaster_cfg = connection.get_file(os.path.join(configs_path, CONFIGS[0]), 'r')
        data_line = ''.join([l for l in mfsmaster_cfg.readlines() \
                                                        if 'DATA_PATH' in l])
        try:
            metafiles_path = re.split(' ?= ?', data_line)[1].strip()
        except IndexError:
            errors['metafiles'].append('Cannot read DATA_PATH option in %s.'\
                                                                 % CONFIGS[0])
        else:
            if connection.path_exists(metafiles_path):
                metafiles = connection.get_files_info(metafiles_path)
            else:
                errors['metafiles'].append(''.join([
                                    '%s does not exist.<br/>' % metafiles_path,
                                    'Change DATA_PATH option in mfsmaster.cfg.']))

    except IOError:
        errors['metafiles'].append(
                        'Cannot find \"%s\" in %s.' % (CONFIGS[0], configs_path)
                        )
    finally:
        mfsmaster_cfg.close()
    
    return metafiles_path, metafiles, errors


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
    return render_template('config_files/edit_config.html',
                           filename = filename,
                           filecontent = content)


def save_config(connection, path, config_name):
    """
    Saves config file with new content.
    Returns empty string for valid flask response.
    """
    try:
        f = connection.get_file(os.path.join(path, config_name), 'w')
    except Exception as e:
        logger.exception(e)
    else:
        content = request.values.get('content', '')
        if content:
            f.write(content)
            logger.info('%s was successfully saved.' % config_name)
    finally:
        f.close()
    return ''


def get_master_info(host, port, errors):
    """
    Returns master host, port and version.
    """
    errors['master_info'] = []
    version = ''
    try:
        mfs = MooseFS(masterhost=host,
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
    
