import argparse
import socket
from app.utils import mfs_exceptions

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

config = ConfigParser()

DEFAULT_BACKUP_PATH = '/var/mfs/backups'
DEFAULT_APP_PORT = 5001

def cli_args_parser():
    parser = argparse.ArgumentParser(description='Parsing CLI args')
    parser.add_argument('-f', action="store", dest='f',
                        help='Path to config file')

    parsed_args = parser.parse_args()
    return parsed_args.f


def config_parser(section):
    data = None
    path = cli_args_parser()

    if path is None:
        config.read('/etc/moosefs_tool/moosefs_tool.ini')
    else:
        config.read(path)
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



ssh_options = config_parser('ssh_options')
moose_options = config_parser('moose_options')
general = config_parser('general')

