# life/plugs/entry.py
#
#

""" record entry of lived events. """

## life imports

from life import O
from life.utils import strtotime

## basic import

import time

## entry callbacks

def entry(event):
    print(event.json())
    t = strtottime(event.input)
    if t: event.enteredtime = t ; event.reply("time set at %s" % time.ctime(t))
    event.save()

entry.cb = "CONSOLE"
