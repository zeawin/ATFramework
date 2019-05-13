# -*- coding: utf-8 -*-

"""
    Effect: The logging filter
"""

import re
import logging


class LinkFilter(logging.Filter):
    """Filtering the console HTML tags
    """
    def __init__(self):
        super(LinkFilter, self).__init__()

    def filter(self, record):
        """override base class function
        """
        pattern = re.compile('<[A-Za-z]{1,4} [^>]+>|</[A-Za-z]{1,4}>', re.I)
        record.msg = pattern.sub('', record.msg)
        return True