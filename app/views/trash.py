from flask import render_template, redirect, request, url_for
from app import app
from app.utils import transport
from app.utils.config_helper import roots
from app.decorators import login_required
from stat import S_ISDIR

import os
import hashlib


@app.route('/trash', methods = ['GET', 'POST'])
@login_required
def trash():
    host = roots['master_host']
    port = roots.get('master_port', 9421)
    con = transport.Connect(host)
    path = '/mnt/mfs-test'
    tree = make_remote_tree(con, path)
    errors = {}
    command = '/usr/bin/mfsmount /mnt/mfs-test -H mfsmaster -o mfsmeta'
    resp = con.remote_command(command, 'stdout')
    if resp:
        errors['mount'] = 'Failed to mount trash folder with command \"%s\".<br/>Got following error:<br/> %s.' % (command, resp)
    return render_template('trash.html',
                           errors = errors,
                           tree = tree,
                           title = 'Trash')


def make_remote_tree(connection, path):
    tree = dict(id=_set_id(path), is_dir=True,
                name=os.path.basename(path), full_name=path,
                children=[])
    try: 
        lst = connection.remote.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if isdir(connection, fn):
                tree['children'].append(make_remote_tree(connection, fn))
            else:
                tree['is_dir'] = False
                tree['children'].append(dict(id=_set_id(fn), name=name,
                                             full_name=fn))
    return tree


def isdir(connection, path):
  try:
    return S_ISDIR(connection.remote.stat(path).st_mode)
  except IOError:
    #Path does not exist, so by definition not a directory
    return False


def _set_id(full_name):
    return hashlib.md5(full_name).hexdigest()