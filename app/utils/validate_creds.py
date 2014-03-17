from app.utils.log_helper import auth
import crypt

def creds_validator(username, password):

    crypted_method = auth['passwd'].split('$')[1]
    crypted_salt = auth['passwd'].split('$')[2]
    cryted_passwd = auth['passwd'].split('$')[3]
    result_str = '{0}{1}{0}{2}{0}'.format('$', crypted_method, crypted_salt)

    crypted_input_passwd = crypt.crypt(password, result_str)

    return  auth['user'] == username and crypted_input_passwd == result_str + cryted_passwd