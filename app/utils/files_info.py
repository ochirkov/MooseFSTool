import os
import time
import datetime


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