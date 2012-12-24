# life/test.py
#
#

""" define core test classes. """

## life imports

import life

## basic imports

import unittest

## Test class

class Test(unittest.TestCase):

    """ class that implements setup and teardow of tests. """

    def __init__(self, *args, **kwargs):
       unittest.TestCase.__init__(self, *args, **kwargs)
       from .log import log_config
       self.logger = log_config("error")