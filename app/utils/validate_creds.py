import crypt
import spwd

def creds_validator(username, password):

    crypted_root_pwd = spwd.getspnam(username).sp_pwd
    crypted_method, crypted_salt = (crypted_root_pwd.split('$')[1], crypted_root_pwd.split('$')[2])
    result_str = '{0}{1}{0}{2}{0}'.format('$', crypted_method, crypted_salt)

    crypted_input_passwd = crypt.crypt(password, result_str)

    return crypted_input_passwd == spwd.getspnam(username).sp_pwd