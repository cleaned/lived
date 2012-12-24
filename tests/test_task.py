# tests/basic.py
#
#

from life import O, test
from life.tasks import TaskRunner, Dispatcher

import unittest

class Test_Tasks(test.Test):

    def test_constructTask(self):
        o = TaskRunner()
        self.assertEqual(type(o), TaskRunner)

    def test_constructDispatcher(self):
        o = Dispatcher()
        self.assertEqual(type(o), Dispatcher)

    def test_cleanpathDispatcher(self):
        o1 = Dispatcher()
        o1.bla = 3
        o2 = O(**o1)
        self.assertEqual(o2.bla, 3)
        