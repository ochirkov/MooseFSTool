import re
import argparse
import socket
import os.path, os.system
from app.utils import mfs_exceptions

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

config = ConfigParser()

DEFAULT_CONFIG_PATH = '/etc/moosefs_tool/moosefs_tool.ini'
DEFAULT_BACKUP_PATH = '/var/mfs/backups'
DEFAULT_APP_PORT = 5001
LOCAL_HOST_ADDR = '127.0.0.1'


def cli_args_parser():
    parser = argparse.ArgumentParser(description='Parsing CLI args')
    parser.add_argument('-f', action="store", dest='f',
                        help='Path to config file')

    parsed_args = parser.parse_args()
    return parsed_args.f


path = cli_args_parser()


def config_parser(section):

    if path is None:
        config.read(DEFAULT_CONFIG_PATH)
    else:
        config.read(path)

    sections_check(config)
    directives_check(config)
    network_check(config)
    resolv_check(config)

    return dict((x, y) for x, y in config.items(section))


def sections_check(config_obj):
    for i in ('general', 'moose_options', 'ssh_options'):
        if not config_obj.has_section(i):
            msg = '%s section is missing. This section is required' % str(i)
            raise mfs_exceptions.SectionMissing(msg)

def directives_check(config_obj):

    # Check whether
    options = {'moose_options': 'master_host', 'ssh_options': 'key'}
    for i in options:
        if not config_obj.has_option(i, options.get(i)):
            msg = '%s value is required for %s directive.' % (options.get(i), i)
            raise mfs_exceptions.ValueError(msg)

    # IP address validation
    ip_for_valid = {'general': 'host', 'moose_options': 'master_host'}
    try:
        for i in ip_for_valid:
            socket.inet_aton(config_obj.get(i, ip_for_valid[i]))
    except Exception:
        msg = '%s ip address is not valid in %s section.' % (ip_for_valid[i], i)
        raise mfs_exceptions.IpAddressValidError(msg)

    # Check whether ssh key exists
    try:
        if path is None:
            os.path.isfile(DEFAULT_CONFIG_PATH)
        else:
            os.path.isfile(path)
    except Exception:
        msg = 'Config file is absent'
        raise mfs_exceptions.ConfigMissing(msg)

    # Check whether backup path exists
    if not os.path.isdir(config_obj.get('moose_options', 'backup_path')):
        msg = 'Backup folder %s is not exists' % config_obj.get('moose_options', 'backup_path')
        raise mfs_exceptions.BackupPathError(msg)


def network_check(config_obj):

    # Check whether app port is accessible
    port = config_obj.get('general', 'port')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if port is None:
        port = DEFAULT_APP_PORT
        result = s.connect_ex((LOCAL_HOST_ADDR, port))
    else:
        result = s.connect_ex((LOCAL_HOST_ADDR, port))

    if result != 0:
        s.close()
        msg = '%s port is already used' % str(port)
        raise mfs_exceptions.PortUsageError(msg)


def resolv_check(config_obj):

    master_host = config_obj.get('moose_options', 'master_host')

    # Check whether master host resolves
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

    if (allowed.match(x) for x in master_host.split(".")):
        try:
            socket.gethostbyname('master_host')
        except Exception:
            msg = "%s doesn't resolve" % str(master_host)
            raise mfs_exceptions.HostResolveError(msg)

    # Check whether master address is valid
    responce = os.system("ping -c 1 " + master_host)

    if responce != 0:
        msg = '%s host is innaccessible' % str(master_host)
        raise mfs_exceptions.MooseConnectionFailed(msg)


ssh_options = config_parser('ssh_options')
moose_options = config_parser('moose_options')
general = config_parser('general')

