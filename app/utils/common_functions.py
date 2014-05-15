"""
author       :  Anastasiia Panchenko
creation date:  27/04/2014

Provides functions that are used several times.
"""

import re

def nl2br(text):
    """
    Returns text, prepeared for html template.
    """
    return text.replace('\n', '<br/>')