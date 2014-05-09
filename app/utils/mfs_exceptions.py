class MooseError(Exception):
    ''' The base MooseFSTool exception from which all others should subclass '''

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class MooseConnectionFailed(MooseError):
    pass

class OpenRemoteFileFailed(MooseError):
    pass

class DataPathGettingFailed(MooseError):
    pass

class ConfigsException(MooseError):
    pass

class MetafilesException(MooseError):
    pass

class SectionMissing(ConfigsException):
    pass

class ValueError(ConfigsException):
    pass

class IpAddressValidError(ConfigsException):
    pass