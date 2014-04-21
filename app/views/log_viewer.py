from flask import render_template, redirect, request, url_for
from app import app
from app.decorators import login_required
from app.utils.config_helper import logging

import re

@app.route('/log_viewer', methods = ['GET', 'POST'])
@login_required
def log_viewer():
    """
    Returns log content with two parameters:
    page:
        0 - all content
        number - page number
    view_direction:
        0 - normal order
        1 - reversed order
    """
    page = 1
    log_file = logging['path']
    with open(log_file, 'r') as log:
        lines = log.readlines()
        start, end = -24, len(lines)
        log_content = [re.sub(r' {2}', r'&nbsp;'*4, line) \
                                    for line in lines[start:end]]
    return render_template('log-viewer.html',
                           page = page,
                           log_file = log_file,
                           log_content = log_content,
                           title = 'Log Viewer')

@app.route('/log_viewer/<page>', methods = ['GET', 'POST'])
@login_required
def log_viewer1(page):
    page = int(page)
    lines_per_page = 20
    log_file = logging['path']
    with open(log_file, 'r') as log:
        lines = log.readlines()
        length = len(lines)
        pag = get_pagination_info(length, int(page)
                                  , lines_per_page)
        if int(page):
            start, end = pag['start'], pag['end']
        else:
            start = 0
            end = len(lines)
        log_content = reversed([re.sub(r' {2}', r'&nbsp;'*4, line) \
                                    for line in lines[start:end]])
    
    return render_template('log-viewer.html',
                           page = page,
                           pages = pag['pages'],
                           next = pag['next'],
                           prev = pag['prev'],
                           log_file = log_file,
                           log_content = log_content,
                           title = 'Log Viewer')


def get_pagination_info(lst_length, page, lines_per_page):
    page = int(page)
    max_pages = 8
    pages = [i+1 for i, n in enumerate(range(0, lst_length, lines_per_page))]
    next = 0
    prev = 0
    if len(pages) > max_pages:
        if page > 0:
            prev = page - 1
        if page < pages[-1]:
            next = page + 1
    start = -lines_per_page*page
    end = start + lines_per_page if start + lines_per_page != 0 else lst_length
    return {'pages' : pages,
            'next' : next,
            'prev' : prev,
            'start' : start,
            'end' : end}