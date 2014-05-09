from app.utils.config_helper import ssh_options
from app.utils import mfs_exceptions
from app.utils.log_helper import logger

import os
import time
import datetime

SSH_USER = 'root'

try:
    import paramiko
except ImportError:
        pass


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

    def __init__(self, host, user=SSH_USER, private_key_file=ssh_options.get('key',None), port=22):

        """
        Init Connect object. Init method understands both ip address and hostname of remote host.
        >>> obj = Connect('127.0.0.1')
        >>> obj = Connect('mfsmaster')
        """
        self.host = host
        self.port = port
        self.user = user
        self.private_key_file = private_key_file
        self.ssh = self.connect()
        self.remote = self._sftp_connect()

    def _connect(self, ssh_client):

        """
        Helper for connect method. According to __init__ arguments (auth type, login, pwd) return appropriate
        ssh connection.
        >>> obj._connect(ssh_client)
        """
        try:
            ssh_client.connect(self.host, username=self.user, key_filename=self.private_key_file)

        except Exception as e:
            msg = "\n".join(['ssh connection failed with the following error:\n%s' % str(e),
                             'CONNECTION DETAILS:',
                             'host: %s' % self.host,
                             'username: %s' % self.user,
                             'private key file: %s' % self.private_key_file])
            logger.error(e)
            raise mfs_exceptions.MooseConnectionFailed(msg)

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

        try:
            sftp = self.ssh.open_sftp()

        except Exception as e:
            msg = "Failed to open sftp session: %s" % str(e)
            logger.error(e)
            raise mfs_exceptions.MooseConnectionFailed(msg)
        return sftp


    def get_file(self, path, mode):

        """
        Return file object related with remote file. Method takes path to the file and mode args.
        >>> obj.get_file('/etc/mfs/mfshdd.cfg', 'w')
        >>> obj.get_file('/etc/mfs/mfshdd.cfg', 'rb')
        """

        try:
            file_o = self.remote.file(path, mode)

        except IOError as e:
            msg = "Failed to open remote file: %s" % str(e)
            logger.error(e)
            raise mfs_exceptions.OpenRemoteFileFailed(msg)
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
    
    def path_exists(self, path):
        """ 
        Returns True if given path exists on remote host.
        >>> obj.path_exists('/home/myuser')
        """
        try:
            self.remote.stat(path)
            return True
        except IOError as e:
            return False
    
    
    @staticmethod
    def _format_time(t):
        """
        Returns time in human readable format. 
        """
        format = "%a %b %d %H:%M:%S %Y"
        return datetime.datetime.strptime(time.ctime(t), format)
    
    
    @staticmethod
    def sizeof_fmt(size):
        for x in ['B','KB','MB','GB','TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0
    
    
    def get_files_info(self, path):
        """
        Returns list with stat file info in path on remote host.
        >>> obj.get_files_info('/home/myuser')
        """
        result = []
        for file in self.remote.listdir(path=path):
            stat = self.remote.stat(os.path.join(path, file))
            result.append({'name'  : file,
                           'mode'  : oct(stat.st_mode),
                           'uid'   : stat.st_uid,
                           'gid'   : stat.st_gid,
                           'size'  : stat.st_size,
                           'atime' : self._format_time(stat.st_atime),
                           'mtime' : self._format_time(stat.st_mtime),
#                            'ctime' : self._format_time(stat.st_ctime)
                        })
        return result


    def ssh_close(self):

        """
        Close ssh session with remote host.
        """
        self.ssh.close()


    def remote_close(self):

        """
        Close sftp session with remote host.
        """

