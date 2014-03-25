from flask import render_template, request
from app.utils import transport

import os
import time
import datetime


def get_configs(host, path):
    con = transport.Connect(host)
    result = []
    config_files = [
                    "mfsexports.cfg", 
                    "mfstopology.cfg",
                    "mfsmaster.cfg"
                 ]
    for file in config_files:
        try:
            f = con.get_file(os.path.join(path, file), 'r')
        except:
            pass
        else:
            result.append(file)
    
    return result


def edit_config(host, path, config_name):
    con = transport.Connect(host)
    filename = os.path.join(path, config_name)
    f = con.get_file(filename, 'r')
    content = f.read()
    return render_template('config_files/edit_config.html',
                           filename = filename,
                           filecontent = content)


def save_config(host, path, config_name):
    con = transport.Connect(host)
    f = con.get_file(os.path.join(path, config_name), 'w')
    content = request.values.get('content', '')
    if content:
        f.write(content)
    return ''


def get_metafiles_info(path):
    lst = []
    format = "%a %b %d %H:%M:%S %Y"
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = \
                                                os.stat(os.path.join(path, file))
            lst.append({'name' : file,
                        'mode' : oct(mode),
                        'uid' : uid,
                        'gid' : gid,
                        'size' : size,
                        'atime' : _format_time(atime, format),
                        'mtime' : _format_time(mtime, format),
                        'ctime' : _format_time(ctime, format)
                        })
    return lst

def _format_time(t, f):
    return datetime.datetime.strptime(time.ctime(t), f)

def sizeof_fmt(size):
    for x in ['B','KB','MB','GB','TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0