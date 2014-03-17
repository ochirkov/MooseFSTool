from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField

class LoginForm(Form):
    login = TextField('login', [validators.Length(min=4, max=15)])
    password = PasswordField('New Password')