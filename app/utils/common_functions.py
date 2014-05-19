"""
author       :  Anastasiia Panchenko
creation date:  27/04/2014

Provides functions that are used several times.
"""

from app.utils.config_helper import moose_options, mfs_exceptions, DEFAULT_MFSMASTER_PORT
from app.utils.moose_lib import MooseFS

import re

def nl2br(text):
    """
    Returns text, prepeared for html template.
    """
    return text.replace('\n', '<br/>')

def mfs_object():
    master_host = moose_options.get('master_host', '')
    master_port = moose_options.get('master_port', DEFAULT_MFSMASTER_PORT)
    errors = []
    result = {'mfs' : None, 'errors' : errors}
    try:
        mfs = MooseFS(masterhost=master_host,
                      masterport=master_port)
        result['mfs'] = mfs
    except mfs_exceptions.MooseConnectionFailed as e:
        errors.append('Error while trying to connect to %s:%s<br/>%s' % (master_host,
                                                                         master_port, e))
    except Exception as e:
        errors.append(str(e))
    result['errors'] = errors
    return result