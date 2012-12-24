# tests/basic.py
#
#

from life import O, test, j

import unittest

class Test_O(test.Test):

    def test_persistrestore(self):
        o1 = O().load(j("default", "test"))
        o1.bla = 3
        o1.save()
        o2 = O().load(j("default", "test"))
        self.assertEqual(o2.bla, 3)

    def test_cleanpathpersistedrestore(self):
        o1 = O().load(j("default", "test"))
        o1.bla = 3
        o1.save()
        o2 = O().load(j("default", "test"))
        o3 = O(**o2)
        self.assertEqual(o3.bla, 3)
        