from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required
from app.utils.files_info import get_configs, edit_config, save_config, get_metafiles_info
from app.utils.log_helper import roots
from app.utils.moose_lib import MooseFS
from collections import OrderedDict

import os

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
    metafiles_path = roots['metafiles']
    metafiles = get_metafiles_info(metafiles_path)
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
                      masterport=port)
        version = mfs.masterversion
    except Exception as e:
        error = 'Error while trying to connect to %s:%s<br/>%s' % (host, port, e)
    return OrderedDict({'Host' : host,
                        'Port' : port,
                        'Version' : version,
                        'Error' : error})
    