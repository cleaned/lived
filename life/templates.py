# life/templates.py
#
#

"""

    W E L C O M E  T O  L I F E !!!

    -=-

"""

## txt templates

# headertxt is written on top of every file put to disk

headertxt = '''# ===========================================================
# L I F E  %s  ->-  %s  (%s)
#
# changed on %s
#
# L I F E can edit this file !!
#
# =============================================================
'''

# plugtxt is the data for the test plugin (written in datadir/plugs). 

plugtxt = '''""" life testing plugin. written on start of L I F E. """

## life imports

from life import O, get_kernel, __version__

## basic imports

import logging
import time

## test command

def test(event):
    """ reply with a json dump of this event. """
    event.reply(event.json(indent=True))

test.cmnd = "test"

def fulljson(event):
    """ reply with a json dump of this event. """
    event.reply(event.full(indent=True))

fulljson.cmnd = "full"

## version command (threaded)

def version(event):
    """ show version. """
    event.reply("L I F E  -=-  P R O T O T Y P E  %s" % __version__)
    event.done()

version.cmnd = "version"
version.threaded = True

## save command

def save(event):
    """ save core of the bot and this event. """
    get_kernel().save()
    event.save()
    event.done()
    event.reply("saved")

save.cmnd = "save"

'''
