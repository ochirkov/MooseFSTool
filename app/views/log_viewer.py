from flask import render_template, redirect, request, url_for
from app import app
from app.utils import transport, config_helper, mfs_exceptions, common_functions
from app.decorators import login_required
from app.utils.log_helper import LOG_PATH, LOG_APP_LABEL, LOG_MFS_LABEL

import re

@app.route('/log_viewer', methods = ['GET'])
@login_required
def log():
    return redirect(url_for('log_viewer', log_type='app', page=1))


@app.route('/log_viewer/<log_type>/<page>', methods = ['GET'])
@login_required
def log_viewer(log_type, page):
    page = int(page)
    pag=0
    lines_per_page=20
    log_content, ret_val, error = '', '', ''
    try:
        ret_val = globals()['get_' + log_type + '_log']()
    except Exception as e:
        error = "Unsupported log file type %s." % log_type
    if isinstance(ret_val, str):
        error = ret_val
    elif isinstance(ret_val, list):
        lines = ret_val
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
    return render_template('log-viewer.html',
                           error = error,
                           pag = pag,
                           log_file = LOG_PATH,
                           log_type = log_type,
                           log_content = log_content,
                           title = 'Log Viewer')


def get_app_log():
    """
    Returns filtered from syslog app lines as list or error as string.
    """
    try:
        log = open(LOG_PATH, 'r')
        lines = filter(lambda x: LOG_APP_LABEL in x, log.readlines())
        return lines
    except Exception as e:
        return "Couldn't open logfile:<br/>%s" % str(e)


def get_mfs_log():
    """
    Returns filtered mfsmaster lines from syslog as list or error as string.
    """
    host = config_helper.moose_options['master_host']
    try:
        con = transport.Connect(host)
        log = con.get_file(LOG_PATH, 'r')
        lines = filter(lambda x: LOG_MFS_LABEL in x and \
                                 LOG_APP_LABEL not in x , log.readlines())
        return lines
    except mfs_exceptions.MooseConnectionFailed as e:
        return common_functions.nl2br(str(e))
    except Exception as e:
        return "Couldn't open remote file %s on host %s<br/>%s" % (LOG_PATH, host, e)
            

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