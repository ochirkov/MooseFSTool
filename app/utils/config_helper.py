"""
authors      :  Oleksandr Chirkov, Anastasiia Panchenko
creation date:  05/04/2014

This module provides with values, parsed from
MFS TOOL config and default values which are used
if are not set in config
"""

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import argparse

DEFAULT_MFSTOOL_CONFIG_PATH = '/etc/moosefs_tool/moosefs_tool.ini'
DEFAULT_BACKUP_PATH = '/var/mfs/backups'
DEFAULT_META_PATH = '/var/lib/mfs'
DEFAULT_CONFIGS_PATH = '/etc/mfs'
DEFAULT_MFSMASTER_PORT = 9421

config = ConfigParser()


def config_parser(section):
    data = None
    path = cli_args_parser()

    if path is None:
        config.read(DEFAULT_MFSTOOL_CONFIG_PATH)
    else:
        config.read(path)
    return dict((x, y) for x, y in config.items(section))


def cli_args_parser():
    parser = argparse.ArgumentParser(description='Parsing CLI args')
    parser.add_argument('-f', action="store", dest='f',
                        help='Path to config file')

    parsed_args = parser.parse_args()
    return parsed_args.f

ssh_options = config_parser('ssh_options')
moose_options = config_parser('moose_options')
general = config_parser('general')

