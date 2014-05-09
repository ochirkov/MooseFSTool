try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import argparse

config = ConfigParser()


def config_parser(section):
    data = None
    path = cli_args_parser()

    if path is None:
        config.read('/etc/moosefs_tool/moosefs_tool.ini')
    else:
        config.read(path)
    return dict((x, y) for x, y in config.items(section))


def cli_args_parser():
    parser = argparse.ArgumentParser(description='Parsing CLI args')
    parser.add_argument('-f', action="store", dest='f',
                        help='Path to config file')

    parsed_args = parser.parse_args()
    return parsed_args.f


general = config_parser('general')
app_wtf = config_parser('app_wtf')
auth = config_parser('auth')
roots = config_parser('roots')
remote_auth = config_parser('remote_auth')
