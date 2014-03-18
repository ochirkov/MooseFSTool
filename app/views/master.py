from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required

import os

@app.route('/master', methods = ['GET', 'POST'])
@login_required
def master():
    path = "/etc/mfs"
    fileslist = [
                 "mfsexports.cfg", 
                 "mfstopology.cfg",
                 "mfsmaster.cfg"
                 ]
    lst = []
    for file in fileslist:
        lst.append(os.path.join(path, file))
    return render_template('master.html',
                           fileslist = lst,
                           title = 'Master')


@app.route('/config_editor', methods = ['GET', 'POST'])
@login_required
def config_editor():
    if request.method == "POST":
        if 'content' not in request.form:
            filename = request.form['filename']
            with open(filename, 'r') as f:
                content = f.read()
        else:
            filename = request.form['filename']
            with open(filename, 'w') as f:
                f.write(request.form['content'])
            return redirect('master')
        return render_template('config_editor.html',
                               filename = filename,
                               filecontent = content,
                               title = 'Master')
    else:
        return redirect('master')