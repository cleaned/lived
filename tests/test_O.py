# tests/basic.py
#
#

from life import O, test

import unittest

class Test_O(test.Test):

    def test_constructO(self):
        o = O()
        self.assertEqual(type(o), O)

    def test_settingattribute(self):
        o = O()
        o.bla = "mekker"
        self.assertEqual(o.bla, "mekker")

    def test_checkattribute(self):
        o = O()
        self.failUnlessRaises(AttributeError)

    def test_underscore(self):
        o = O()
        o._bla = "mekker"
        self.assertEqual(o._bla, "mekker")

    def test_cleanpath(self):
        o1 = O()
        o1.bla = 3
        o2 = O(**o1)
        self.assertEqual(o2.bla, 3)
        