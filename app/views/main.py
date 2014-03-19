from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required

import os

@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))


@app.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    path = '/usr/local'
    tree = make_tree(path)
    return render_template('home.html',
                           tree = tree,
                           path = path,
                           title = 'Home')


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

import hashlib

def _set_id(full_name):
    return hashlib.md5(full_name).hexdigest()