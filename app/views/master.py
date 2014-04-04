from flask import render_template, redirect, request, url_for
from app import app
from app.forms import BackupForm
from app.decorators import login_required
from app.utils import transport
from app.utils.files_info import get_configs, edit_config, save_config, get_metafiles_info
from app.utils.files_info import CONFIGS
from app.utils.config_helper import roots
from app.utils.backup_helper import create_targz
from app.utils.moose_lib import MooseFS
from collections import OrderedDict

import os
import re

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    host = roots['master_host']
    port = roots.get('master_port', 9421)
    configs_path = roots['configs']
    backup_form = BackupForm(request.form)
    configs = get_configs(host, configs_path)
    
    with open(os.path.join(configs_path, CONFIGS[0])) as mfsmaster_cfg:
        data_line = ''.join([l for l in mfsmaster_cfg.readlines() if 'DATA_PATH' in l])
        try:
            metafiles_path = re.split(' ?= ?', data_line)[1].strip()
        except IndexError:
            metafiles_path = ''
        metafiles = get_metafiles_info(metafiles_path) \
                                    if os.path.exists(metafiles_path) else []

    if request.method == 'POST':
        if 'action' in request.values:
            # save or edit config
            action = request.values['action']
            return globals()[action + '_config'](host, configs_path,
                                                 request.values['config_name'])
        else:
            # backup request
            path = backup_form.path.data
            con = transport.Connect(host)
            if con.remote_path_exists(path):
                create_targz(path, metafiles_path)
                return redirect(url_for('master'))
            else:
                backup_form.path.errors += ('This path does not exist.',)

    return render_template('master.html',
                           configs_path = configs_path,
                           configs = configs,
                           metafiles_path = metafiles_path,
                           metafiles = metafiles,
                           base_info = get_master_info(host, port),
                           backup_form = backup_form,
                           title = 'Master')


def get_master_info(host, port):
    error = ''
    version = ''
    try:
        mfs = MooseFS(masterhost=host,
                      masterport=int(port))
        version = mfs.masterversion
    except Exception as e:
        error = 'Error while trying to connect to %s:%s<br/>%s' % (host, port, e)
    return OrderedDict({'Host' : host,
                        'Port' : port,
                        'Version' : version,
                        'Error' : error})
    
