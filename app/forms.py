from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField

class LoginForm(Form):
    
    username = TextField(label='login',
                      validators=[validators.Length(min=4, max=15),
                                  validators.Required()])
    password = PasswordField(label='password',
                             validators=[validators.Required()])
