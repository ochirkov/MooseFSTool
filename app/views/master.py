from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required
from app.utils.files_info import get_configs, edit_config, save_config, get_metafiles_info
from app.utils.files_info import CONFIGS
from app.utils.config_helper import roots
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
    if request.method == 'POST':
        action = request.values['action'] # save or edit
        return globals()[action + '_config'](host, configs_path,
                                             request.values['config_name'])
    
    configs = get_configs(host, configs_path)
    
    with open(os.path.join(configs_path, CONFIGS[0])) as mfsmaster_cfg:
#         pattern = re.compile('(?!DATA_PATH ?= ?)(\/\w+)+(\r\n)+')
        data_line = ''.join([l for l in mfsmaster_cfg.readlines() if 'DATA_PATH' in l])
        try:
            metafiles_path = re.split(' ?= ?', data_line)[1].rstrip() # also need to replace spaces and tabs
        except IndexError:
            metafiles_path = ''
        metafiles = get_metafiles_info(metafiles_path) \
                                    if os.path.exists(metafiles_path) else []
    return render_template('master.html',
                           configs_path = configs_path,
                           configs = configs,
                           metafiles_path = metafiles_path,
                           metafiles = metafiles,
                           base_info = get_master_info(host, port),
                           title = 'Master')


def get_master_info(host, port):
    error = ''
    version = '0.0.0'
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
    
