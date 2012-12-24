# life/plugs/context.py
#
#

""" show context. """

## basic import 

import sys

## context command

def context(event):
    result = []
    frame = sys._getframe()
    code = frame.f_back.f_code
    for i in dir(code): print("%s => %s" % (i, getattr(code, i)))
    del frame

context.cmnd = "context"
