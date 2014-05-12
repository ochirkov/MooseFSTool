from wtforms import Form, TextField, validators, PasswordField
from app.utils.config_helper import moose_options, DEFAULT_BACKUP_PATH


class LoginForm(Form):
    
    username = TextField(label='login',
                         default='root',
                      validators=[validators.Length(min=4, max=15),
                                  validators.Required()])
    password = PasswordField(label='password',
                             validators=[validators.Required()])

class BackupForm(Form):
    
    path = TextField(label='path to backup',
                     default = moose_options.get('backup_path', DEFAULT_BACKUP_PATH),
                     validators=[validators.Required()])
