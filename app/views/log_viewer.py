from flask import render_template, redirect, request, url_for
from app import app
from app.utils import transport, config_helper, mfs_exceptions, useful_functions
from app.decorators import login_required
from app.utils.log_helper import LOG_TYPE, LOG_PATH, LOG_APP_LABEL, LOG_MFS_LABEL

import re

@app.route('/log_viewer', methods = ['GET'])
@login_required
def log():
    return redirect(url_for('log_viewer', log_var='app', page=1))

@app.route('/log_viewer/<log_var>/<page>', methods = ['GET'])
@login_required
def log_viewer(log_var, page):
    pag, log_content, errors = globals()[log_var + '_log_content'](int(page))
    return render_template('log-viewer.html',
                           errors = errors,
                           pag = pag,
                           log_file = LOG_PATH,
                           log_var = log_var,
                           log_content = log_content,
                           title = 'Log Viewer')

def app_log_content(page, pag=0, lines_per_page=20, errors={}):
    log_content = ''
    try:
        with open(LOG_PATH, 'r') as log:
            lines = log.readlines()
            if LOG_TYPE == 'syslog':
                lines = filter(lambda x: LOG_APP_LABEL in x, lines)
            l = len(lines)
            pag = get_pagination_info(page, l, lines_per_page)
            if page == 0: # show full log
                start = 0
                end = l
            elif page > 0 and page <= pag['last']:
                start, end = get_indexes(page, l, lines_per_page)
            else: # page is out of range
                return redirect(url_for('log_viewer', page=1))
            log_content = list(reversed([re.sub(r' {2}', r'&nbsp;'*4, line) \
                                        for line in lines[start:end]]))
    except Exception as e:
        errors['logfile'] = "Couldn't open logfile:<br/>%s" % str(e)
    return pag, log_content, errors

def mfs_log_content(page, pag=0, lines_per_page=20, errors={}):
    host = config_helper.roots['master_host']
    log_path = '/var/log/syslog'
    log_content = ''
    try:
        con = transport.Connect(host)
    except mfs_exceptions.MooseConnectionFailed as e:
        errors['connection'] = (useful_functions.nl2br(str(e)), )
    else:
        if con.path_exists(log_path):
            log = con.get_file(log_path, 'r')
            lines = log.readlines()
            lines = filter(lambda x: LOG_MFS_LABEL in x, lines)
            l = len(lines)
            pag = get_pagination_info(page, l, lines_per_page)
            if page == 0: # show full log
                start = 0
                end = l
            elif page > 0 and page <= pag['last']:
                start, end = get_indexes(page, l, lines_per_page)
            else: # page is out of range
                return redirect(url_for('log_viewer', page=1))
            log_content = list(reversed([re.sub(r' {2}', r'&nbsp;'*4, line) \
                                        for line in lines[start:end]]))
        else:
            errors['logfile'] = "Couldn't open logfile %s on host %s" % (log_file, host)
    return pag, log_content, errors

def get_indexes(page, lines_amount, lines_per_page):
    """
    Returns:
    start, end - list indexes for slicing of a list with lines from input file
    """
    start = -lines_per_page*page
    end = start + lines_per_page if start + lines_per_page != 0 else lines_amount
    return start, end

def get_pagination_info(page, lines_amount, lines_per_page):
    """
    Input: page - current page, lines_amount - number of lines in file,
    lines_per_page - amount of lines that should be on one page
    
    Returns dictionary with keys:
    pages - list with page numbers, page - current page, last - number of last page
    prev, next - previous and next page numbers. If prev is 0, "Prev" link is
                 disabled; if next is 0, "Next" link is disabled
    """
    pages = [i+1 for i, n in enumerate(range(0, lines_amount, lines_per_page))]
    last = pages[-1] if pages else 1
    prev = page-1
    if page < last:
        next = page + 1
    else:
        next = 0
    return {'pages' : pages,
            'page' : page,
            'next' : next,
            'prev' : prev,
            'last' : last}