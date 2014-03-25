import paramiko
from app.utils.log_helper import remote_auth

class Connect(object):

    '''
    Connect class provides SSH connect via Paramiko module. Connection could init via login/pwd, key/pwd or 
    key without pwd. Once you've created Connect object you can get ssh connect to remote machine
    and sftp connection. It also provides remote file interface.

    >>> obj = Connect('127.0.0.1')  # Init object
    >>> obj.ssh  # SSH connection
    >>> obj.remote  # SFTP client
    >>> obj.get_file('path_to_file', 'r')  # Will get you remote file object
    >>> obj.ssh_close()  # Close ssh session
    >>> obj.remote_close()  # Close sftp session
    '''

    def __init__(self, host, user=remote_auth.get('user'), password=remote_auth.get('passwd', None),
                 private_key_file=remote_auth.get('key',None), port=22):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.remote_auth_type = remote_auth.get('auth_type')
        self.remote_auth_passwd = remote_auth.get('passwd')
        self.ssh = self.connect()
        self.remote = self._sftp_connect()

    def _connect(self, ssh_client):

        if self.remote_auth_type == 'pwd':
            ssh_client.connect(self.host, username=self.user, password=self.password)

        elif self.remote_auth_type == 'key':
            if self.remote_auth_passwd:
                ssh_client.connect(self.host, username=self.user, key_filename=self.private_key_file,
                                   password=self.password)
            else:
                ssh_client.connect(self.host, username=self.user, key_filename=self.private_key_file)

        return ssh_client


    def connect(self):

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        return self._connect(client)


    def _sftp_connect(self):

        sftp = self.ssh.open_sftp()

        return sftp


    def get_file(self, path, mode):

        file_o = self.remote.file(path, mode)

        return file_o


    def ssh_close(self):

        self.ssh.close()


    def remote_close(self):

        self.remote.close()

