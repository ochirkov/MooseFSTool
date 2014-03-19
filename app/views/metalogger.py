from flask import render_template, redirect, request, url_for
from app import app
from app.forms import LoginForm
from app.decorators import login_required

import os

@app.route('/metalogger', methods = ['GET', 'POST'])
@login_required
def metalogger():
    lst = []
    path = '/var/lib/mfs/'
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = \
                                                os.stat(os.path.join(path, file))
            lst.append({'name' : file,
                        'mode' : oct(mode),
                        'uid' : uid,
                        'gid' : gid,
                        'size' : size,
                        'atime' : atime,
                        'mtime' : mtime,
                        'ctime' : ctime
                        })
            
    return render_template('metalogger.html',
                           fileslist = lst,
                           title = 'Metalogger')