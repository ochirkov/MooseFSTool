from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required
from app.utils.files_info import get_configs, get_metafiles_info
from app.utils.config_helper import roots

import os

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    configs_path = roots['configs']
    configs = get_configs(configs_path)
    metafiles_path = roots['metafiles']
    metafiles = get_metafiles_info(metafiles_path)
    return render_template('master.html',
                           configs_path = configs_path,
                           configs = configs,
                           metafiles_path = metafiles_path,
                           metafiles = metafiles,
                           title = 'Master')


@app.route('/config_editor/<config_name>', methods = ['GET', 'POST'])
@login_required
def config_editor(config_name):
    path = roots['configs']
    filename = os.path.join(path, config_name + '.cfg')
    if request.method == 'POST':
        with open(filename, 'w') as f:
            f.write(request.form['content'])
        return redirect('master')
    
    with open(filename, 'r') as f:
        content = f.read()
    return render_template('config_editor.html',
                           filename = filename,
                           filecontent = content,
                           title = 'Master')