from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required

import os

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    fileslist = [
                 ("mfsexports", "mfsexports.cfg"), 
                 ("mfstopology", "mfstopology.cfg"),
                 ("mfsmaster", "mfsmaster.cfg")
                 ]
    lst = []
    for file in fileslist:
        lst.append(file)
    return render_template('master.html',
                           fileslist = lst,
                           title = 'Master')


@app.route('/config_editor/<config_name>', methods = ['GET', 'POST'])
@login_required
def config_editor(config_name):
    path = "/etc/mfs"
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