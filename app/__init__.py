from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bla'

from app.views import home, login, master, metaloggers, chunkservers, clients, data, trash, log_viewer
