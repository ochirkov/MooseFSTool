import paramiko
from app.utils.log_helper import remote_auth

class Connect(object):

    '''
    Connect class provides SSH connect via Paramiko module. Connection could init via login/pwd, key/pwd or just key.
    Once you've create Connect object you can get ssh connect to remote machine
    and sftp connection. It also provides remote file interface.

    >>> obj = Connect('127.0.0.1')  # Init object
    >>> obj.ssh  # SSH connection
    >>> obj.remote  # SFTP client
    >>> obj.get_file('path_to_file', 'r')  # Will get you remote file object
    >>> obj.ssh_close()  # Close ssh session
    >>> obj.remote_close()  # Close sftp session
    >>> obj.remote_command('ls -l', 'stdout')  # Execute command on remote host and return code/stdout
    '''

    def __init__(self, host, user=remote_auth.get('user'), password=remote_auth.get('passwd', None),
                 private_key_file=remote_auth.get('key',None), port=22):

        """
        Init Connect object. Init method understands both ip address and hostname of remote host.
        >>> obj = Connect('127.0.0.1')
        >>> obj = Connect('mfsmaster')
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.private_key_file = private_key_file
        self.remote_auth_type = remote_auth['auth_type']
        self.remote_auth_passwd = remote_auth['passwd']
        self.ssh = self.connect()
        self.remote = self._sftp_connect()

    def _connect(self, ssh_client):

        """
        Helper for connect method. According to __init__ arguments (auth type, login, pwd) return appropriate
        ssh connection.
        >>> obj._connect(ssh_client)
        """

        if self.remote_auth_type == 'pwd':
            ssh_client.connect(self.host, username=self.user, password=self.password)

        elif self.remote_auth_type == 'key':
            if not self.remote_auth_passwd:
                ssh_client.connect(self.host, username=self.user, key_filename=self.private_key_file)

            elif self.remote_auth_type == 'key' and self.remote_auth_passwd:
                ssh_client.connect(self.host, username=self.user, key_filename=self.private_key_file,
                                   password=self.password)

        return ssh_client


    def connect(self):

        """
        connect method call _connect and pass him ssh_client. It returns ssh connection with remote host.
        >>> obj.connect()
        """

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        return self._connect(client)


    def _sftp_connect(self):

        """
        Helper method. It initialize sftp connection with remote host.
        >>> obj._sftp_connect()
        """

        sftp = self.ssh.open_sftp()

        return sftp


    def get_file(self, path, mode):

        """
        Return file object related with remote file. Method takes path to the file and mode args.
        >>> obj.get_file('/etc/mfs/mfshdd.cfg', 'w')
        >>> obj.get_file('/etc/mfs/mfshdd.cfg', 'rb')
        """

        file_o = self.remote.file(path, mode)

        return file_o


    def remote_command(self, cmd, return_value='code'):

        """
        Executes command on remote host via ssh, wait till command will finish work and return code/stdout.
        >>> obj.remote_command('ls -l', 'code')
        >>> obj.remote_command('ls -l', 'stdout')
        """

        ssh_client = self.ssh
        stdin, stdout, stderr = ssh_client.exec_command(cmd)

        if return_value == 'code':
            return stdout.channel.recv_exit_status()
        elif return_value == 'stdout':
            return stdout.readlines()


    def ssh_close(self):

        """
        Close ssh session with remote host.
        """
        self.ssh.close()


    def remote_close(self):

        """
        Close sftp session with remote host.
        """

        self.remote.close()