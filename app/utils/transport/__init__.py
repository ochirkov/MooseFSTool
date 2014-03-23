import paramiko
from app.utils.log_helper import remote_auth

class Connect(object):

    '''
    Connect class...
    '''

    def __init__(self, host, user, password=, private_key_file, port=22):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file


    # def _connect(self, **kwargs):
    #
    #     if remote_auth['auth_type'] == 'key':
    #
    #
    #
    # def connect(self):
    #
    #     client = paramiko.SSHClient()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     connect_params = _connect(remote_auth)
    #     client.connect(self.host, username=self.user, password=self.password)
    #
    #     return client
