from flask import Flask
from app.utils.config_helper import app_wtf, general

app = Flask(__name__)

app.config['CSRF_ENABLED'] = app_wtf['csrf_enabled']
app.config['SECRET_KEY'] = app_wtf['secret_key']


from app.views import home, login, master, metaloggers, chunkservers, clients, data
