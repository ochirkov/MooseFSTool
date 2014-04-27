from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.config_helper import logging

import re

@app.route('/log_viewer', methods = ['GET'])
@login_required
def log():
    return redirect(url_for('log_viewer', page=1))

@app.route('/log_viewer/<page>', methods = ['GET'])
@login_required
def log_viewer(page):
    page = int(page)
    lines_per_page = 20
    log_file = logging['path']
    with open(log_file, 'r') as log:
        lines = log.readlines()
        l = len(lines)
        pag = get_pagination_info(page, l, lines_per_page)
        if page == 0: # show full log
            start = 0
            end = l
        elif page > 0 and page <= pag['last']:
            start, end = get_indexes(page, l, lines_per_page)
        else: # page is out of range
            return redirect(url_for('log_viewer', page=1))
        log_content = reversed([re.sub(r' {2}', r'&nbsp;'*4, line) \
                                    for line in lines[start:end]])
    
    return render_template('log-viewer.html',
                           pag = pag,
                           log_file = log_file,
                           log_content = log_content,
                           title = 'Log Viewer')

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
    last = pages[-1]
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