"""
author       :  Anastasiia Panchenko
creation date:  05/04/2014

This module provides functions for archiving and 
creating backups.
"""

from app import app
from app.utils.log_helper import logger

import tarfile
import datetime
import os

def create_targz(path_to_archive, source_data, suffix='backup'):
    """
    Returns .tar.gz archive with 'source_data' (file, directory, etc.),
    stored in 'path_to_archive'.
    Archive name consists of timestamp in format '%d%m%Y-%H%M%S', suffix and 
    extension 'tar.gz'. 
    E.g.: 05042014_152340_backup.tar.gz
    """
    archive_name = os.path.join(path_to_archive,
                                datetime.datetime.now().strftime("%d%m%Y-%H%M%S") + \
                                '_' + suffix + '.tar.gz')
    try:
        tar = tarfile.open(archive_name, "w:gz")
    except Exception as e:
        logger.exception(e)
        return str(e)
    else:
        tar.add(source_data)
        logger.info('Backup \"%s\" was successfully created.' % archive_name)
        tar.close()
        return ''
        