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
    tree = make_tree('/usr/local')
    return render_template('home.html',
                           tree = tree,
                           title = 'Home')


def make_tree(path, id=''):
    tree = dict(id=id, is_dir=True, name=os.path.basename(path), children=[])
    try: 
        lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            id = _set_id()
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn, id))
            else:
                tree['is_dir'] = False
                tree['children'].append(dict(id=id, name=name))
    return tree

import random
import string

def _set_id():
    digits = "".join( [random.choice(string.digits) for i in xrange(8)] )
    chars = "".join( [random.choice(string.letters) for i in xrange(15)] )
    return digits + chars