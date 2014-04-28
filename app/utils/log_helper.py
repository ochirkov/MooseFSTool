import logging
from logging.handlers import SysLogHandler
from logging import FileHandler, Formatter
from app.utils.config_helper import logging as LOG

LOG_TYPE = LOG.get('type')
LOG_PATH = LOG.get('path', '/var/log/moosetool.log') \
                if LOG_TYPE == 'file' else '/var/log/syslog'

def get_logger():

    """
       get_logger function provides logging object with file/syslog handlers.
       Path to local Moose log file could be obtained from Moose app config.
       By default this path is /var/log/moosetool.log. In [logging] section in app's config
       there is ability to specify appropriate type of logging for you (file, syslog, both types).
    """

    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    if LOG_TYPE == 'file':
        formatter = Formatter('%(asctime)s - - %(name)s: %(levelname)s %(message)s')
        log_handler = FileHandler(filename=LOG_PATH)
    elif LOG_TYPE == 'syslog':
        formatter = Formatter('%(asctime)s moosefstool - - %(name)s: %(levelname)s %(message)s')
        log_handler = SysLogHandler(address='/dev/log')

    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    return logger

logger = get_logger()