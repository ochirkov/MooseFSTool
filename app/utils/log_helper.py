import logging
from logging.handlers import SysLogHandler
from logging import Formatter

LOG_PATH = '/var/log/syslog'

LOG_APP_LABEL = 'moosefstool'
LOG_MFS_LABEL = 'mfsmaster'

def get_logger():

    """
       get_logger function provides logging object with file/syslog handlers.
       Path to local Moose log file could be obtained from Moose app config.
       By default this path is /var/log/moosetool.log. In [logging] section in app's config
       there is ability to specify appropriate type of logging for you (file, syslog, both types).
    """

    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    formatStr = '%(asctime)s {0} - - %(name)s: %(levelname)s %(message)s'.format(LOG_APP_LABEL)
    formatter = Formatter(formatStr)
    log_handler = SysLogHandler(address='/dev/log')

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger

logger = get_logger()