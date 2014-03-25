from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required
from app.utils import transport
from app.utils.files_info import get_metafiles_info
from app.utils.log_helper import roots

import os

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    host = roots['master_host']
    configs_path = roots['configs']
    if request.method == 'POST':
        action = request.values['action'] # save or edit
        return globals()[action + '_config'](host, configs_path,
                                             request.values['config_name'])
    
    configs = get_configs(host, configs_path)
    metafiles_path = roots['metafiles']
    metafiles = get_metafiles_info(metafiles_path)
    return render_template('master/master.html',
                           configs_path = configs_path,
                           configs = configs,
                           metafiles_path = metafiles_path,
                           metafiles = metafiles,
                           title = 'Master')


def get_configs(host, path):
    con = transport.Connect(host)
    result = []
    config_files = [
                    "mfsexports.cfg", 
                    "mfstopology.cfg",
                    "mfsmaster.cfg"
                 ]
    for file in config_files:
        try:
            f = con.get_file(os.path.join(path, "mfsexports.cfg"), 'a')
        except:
            pass
        else:
            result.append(file)
    
    return result


def edit_config(host, path, config_name):
    con = transport.Connect(host)
    filename = os.path.join(path, config_name)
    f = con.get_file(filename, 'r')
    content = f.read()
    return render_template('master/edit_config.html',
                           filename = filename,
                           filecontent = content)


def save_config(host, path, config_name):
    con = transport.Connect(host)
    f = con.get_file(os.path.join(path, config_name), 'w')
    content = request.values.get('content', '')
    if content:
        f.write(content)
    return ''