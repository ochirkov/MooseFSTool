from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required


@app.route('/metaloggers', methods = ['GET', 'POST'])
@login_required
def metaloggers():
    metaloggers = [{'ip':'192.168.56.13' + str(i),
                    'name' : 'metalogger',
                    'status' : 'ok' if i%2==0 else 'dead'} for i in range(10)]
    return render_template('servers-info.html',
                           servers = metaloggers,
                           title = 'Metaloggers')