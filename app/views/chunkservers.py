from flask import render_template, redirect, request, url_for, jsonify
from app import app
from app.decorators import login_required


@app.route('/chunkservers', methods = ['GET', 'POST'])
@login_required
def chunkservers():
    chunkservers = [{'ip':'192.168.56.13' + str(i),
                    'name' : 'chunkserver',
                    'status' : 'ok' if i%2==0 else 'dead'} for i in range(10)]
    return render_template('servers-info.html',
                           servers = chunkservers,
                           title = 'Chunkservers')

