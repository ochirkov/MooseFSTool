from flask import render_template, redirect, request, url_for
from app import app
from app.utils import transport, config_helper, mfs_exceptions, useful_functions
from app.decorators import login_required
from app.views.data import make_remote_tree

@app.route('/trash', methods = ['GET', 'POST'])
@login_required
def trash():
    tree = None
    errors = {}
    host = config_helper.roots['master_host']
    port = config_helper.roots.get('master_port', 9421)
    try:
        con = transport.Connect(host)
    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = (useful_functions.nl2br(str(e)), )
    except Exception as e:
        pass
    else:
        path = '/mnt/mfs-test'
        tree = make_remote_tree(con, path)
        
        command = '/usr/bin/mfsmount /mnt/mfs-test -H mfsmaster -o mfsmeta'
        resp = con.remote_command(command, 'stdout')
        if resp:
            errors['mount'] = 'Failed to mount trash folder with command \"%s\".<br/>Got following error:<br/> %s.' % (command, resp)
        
        if request.method == 'POST':
            return render_template('data/files_items.html',
                                   tree = make_remote_tree(con, request.values['full_name']))
    
    return render_template('trash.html',
                           errors = errors,
                           tree = tree,
                           title = 'Trash')