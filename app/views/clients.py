from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.config_helper import moose_options
from app.utils.moose_lib import MooseFS



@app.route('/clients', methods = ['GET', 'POST'])
@login_required
def clients():
    clients = [{'ip':'192.168.56.13' + str(i),
                    'name' : 'client',
                    'status' : 'ok' if i%2==0 else 'dead'} for i in range(10)]
    return render_template('servers-info.html',
                           servers = clients,
                           title = 'Clients')
    