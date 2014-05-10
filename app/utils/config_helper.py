import re
import argparse
import socket
import os
from app.utils import mfs_exceptions
from app.utils.log_helper import logger

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

config = ConfigParser()

DEFAULT_BACKUP_PATH = '/var/mfs/backups'
DEFAULT_APP_PORT = 5001
DEFAULT_APP_ADDRESS = '0.0.0.0'
DEFAULT_CONFIG_PATH = '/etc/moosefs_tool/moosefs_tool.ini'

def cli_args_parser():
    parser = argparse.ArgumentParser(description='Parsing CLI args')
    parser.add_argument('-f', action="store", dest='f',
                        help='Path to config file')

    parsed_args = parser.parse_args()
    return parsed_args.f


def config_parser(section):

    path = cli_args_parser()

    if path is None:
        config.read(DEFAULT_CONFIG_PATH)
    else:
        config.read(path)

    for i in (sections_check, directives_check, network_check, resolv_check):
        i(config)

    return dict((x, y) for x, y in config.items(section))


def sections_check(config_obj):
    for i in ('general', 'moose_options', 'ssh_options'):
        if not config_obj.has_section(i):
            msg = '%s section is missing. This section is required' % str(i)
            logger.error(msg)
            raise mfs_exceptions.SectionMissing(msg)

def directives_check(config_obj):

    # Check whether
    options = {'moose_options': 'master_host', 'ssh_options': 'key'}
    for i in options:
        if not config_obj.has_option(i, options.get(i)):
            msg = '%s value is required for %s directive.' % (options.get(i), i)
            logger.error(msg)
            raise mfs_exceptions.ValueError(msg)

    # Check whether ssh key exists
    if config_obj.get('ssh_options', 'key') is None:
        msg = 'SSH key file is absent'
        logger.error(msg)
        raise mfs_exceptions.KeyFileMissing(msg)
    else:
        try:
            os.path.isfile(config_obj.get('ssh_options', 'key'))
        except Exception:
            msg = 'Config file is absent'
            logger.error(msg)
            raise mfs_exceptions.InvalidKeyFile(msg)

    # Check whether backup path exists
    try:
        if config_obj.get('moose_options', 'backup_path') is None:
            if not os.path.isdir(DEFAULT_BACKUP_PATH):
                os.makedirs(DEFAULT_BACKUP_PATH)
                msg = 'Backup folder %s is not exists. Creating default backup folder...'
                logger.error(msg)
        else:
            if not os.path.isdir(config_obj.get('moose_options', 'backup_path')):
                msg = 'Backup folder %s is not exists. Creating backup folder...' % config_obj.get('moose_options','backup_path')
                os.makedirs(config_obj.get('moose_options', 'backup_path'))
                logger.error(msg)
    except Exception:
        msg = 'Error during backup folder creation'
        logger.error(msg)
        raise mfs_exceptions.BackupPathError(msg)


def network_check(config_obj):

    # Check whether app port is accessible
    port = config_obj.get('general', 'port')
    address = config_obj.get('general', 'host')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if port is None and address is None:
        port = DEFAULT_APP_PORT
        address = DEFAULT_APP_ADDRESS
        result = s.connect_ex((DEFAULT_APP_ADDRESS, int(port)))
    elif port is None and address is not None:
        port = DEFAULT_APP_PORT
        result = s.connect_ex((address, DEFAULT_APP_PORT))
    else:
        address = DEFAULT_APP_ADDRESS
        result = s.connect_ex((DEFAULT_APP_ADDRESS, int(port)))

    if result == 0:
        s.close()
        msg = '%s port is already used' % str(port)
        logger.error(msg)
        raise mfs_exceptions.PortUsageError(msg)


def resolv_check(config_obj):

    # Addresses validation
    ip_pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    name_pattern = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

    address_for_valid = {'general': 'host', 'moose_options': 'master_host'}

    if config_obj.get('general', 'host') is not None:
        for i in address_for_valid:
            if not ip_pattern.match(config_obj.get(i, address_for_valid[i])):
                if not name_pattern.match(config_obj.get(i, address_for_valid[i])):
                    msg = '%s address is not valid in %s section.' % (address_for_valid[i], i)
                    logger.error(msg)
                    raise mfs_exceptions.AddressValidError(msg)
                else:
                    try:
                        socket.gethostbyname(config_obj.get(i, address_for_valid[i]))
                    except Exception:
                        msg = "%s doesn't resolve" % str(config_obj.get(i, address_for_valid[i]))
                        logger.error(msg)
                        raise mfs_exceptions.HostResolveError(msg)

    # Check whether master address is valid
    master_host = config_obj.get('moose_options', 'master_host')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((master_host, 22))
    except Exception:
        msg = '%s host is innaccessible' % str(master_host)
        logger(msg)
        raise mfs_exceptions.MooseConnectionFailed(msg)
    finally:
        s.close()


ssh_options = config_parser('ssh_options')
moose_options = config_parser('moose_options')
general = config_parser('general')

