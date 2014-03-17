from ConfigParser import ConfigParser
import argparse

config = ConfigParser()


def config_parser(section):
    data = None
    path = cli_args_parser()

    if path is None:
        config.read('/etc/moosefs_tool/moosefs_tool.ini')
    else:
        config.read(path)
    if section == 'general':
        data = dict((x, y) for x, y in config.items('general'))
    elif section == 'app_wtf':
        data = dict((x, y) for x, y in config.items('app_wtf'))
    elif section == 'auth':
        data = dict((x, y) for x, y in config.items('auth'))
    return data


def cli_args_parser():
    parser = argparse.ArgumentParser(description='Parsing CLI args')
    parser.add_argument('-f', action="store", dest='f',
                        help='Path to config file')

    parsed_args = parser.parse_args()
    return parsed_args.f


general = config_parser('general')
app_wtf = config_parser('app_wtf')
auth = config_parser('auth')