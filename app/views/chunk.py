from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.forms import LoginForm
from app.decorators import login_required

import os
import hashlib


@app.route('/chunk', methods = ['GET', 'POST'])
@login_required
def chunk():
    path = '/usr/local'
    tree = make_tree(path)
    if request.method == "POST":
        action = request.values['action']
        data = ''
        if action == 'mfsfileinfo':
            data = 'mfsfileinfo'
        elif action == 'mfscheckfile':
            data = 'mfscheckfile'
        elif action == 'mfsdirinfo':
            data = 'mfsdirinfo'
        return render_template('getinfo.html',
                               full_name = request.values['full_name'],
                               is_dir = request.values['is_dir'],
                               action = action,
                               data = data
                               )
    return render_template('chunk.html',
                           tree = tree,
                           path = path,
                           title = 'Chunk')


@app.route('/chunk/getinfo/<file_id>', methods = ['GET', 'POST'])
@login_required
def get_info(file_id):
    return render_template('getinfo.html',
                           file_id=file_id)

def make_tree(path):
    tree = dict(id=_set_id(path), is_dir=True,
                name=os.path.basename(path), full_name=path,
                children=[])
    try: 
        lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['is_dir'] = False
                tree['children'].append(dict(id=_set_id(fn), name=name,
                                             full_name=fn))
    return tree


def _set_id(full_name):
    return hashlib.md5(full_name).hexdigest()