# life/plugs/frame.py
#
#

""" dump frame data. """

## life imports

from life.utils import dump_frame

## frame import

def frame(event):
    event.reply(dump_frame().json(indent=True))

frame.cmnd = "frame"
frame.perms = ["OPER", ]
