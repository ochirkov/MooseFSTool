from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField
from app.utils.config_helper import roots

class LoginForm(Form):
    
    username = TextField(label='login',
                         default='root',
                      validators=[validators.Length(min=4, max=15),
                                  validators.Required()])
    password = PasswordField(label='password',
                             validators=[validators.Required()])

class BackupForm(Form):
    
    path = TextField(label='path to backup',
                     default = roots.get('backup_path', ''),
                      validators=[validators.Required()])
