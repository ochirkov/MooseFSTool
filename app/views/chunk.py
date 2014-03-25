from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.log_helper import roots
from app.utils.files_info import get_configs, edit_config, save_config, get_metafiles_info

@app.route('/chunk', methods = ['GET', 'POST'])
@login_required
def chunk():
    host = '192.168.56.112'
    configs_path = roots['configs']
    if request.method == 'POST':
        action = request.values['action'] # save or edit
        return globals()[action + '_config'](host, configs_path,
                                             request.values['config_name'])
    configs = get_configs(host, configs_path)
    metafiles_path = roots['metafiles']
    metafiles = get_metafiles_info(metafiles_path)
    return render_template('chunk.html',
                           configs_path = configs_path,
                           configs = configs,
                           metafiles_path = metafiles_path,
                           metafiles = metafiles,
                           base_info = {},
                           title = 'Chunk')
