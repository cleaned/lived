# life/cmnds.py
#
# life monitoring software

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)

"""

## life imports

from life import O

## basic imports

import logging
import types

## hold the commands

class Commands(O):

    """ holds the commands executable on L I F E. """

    def keys(self): return [x for x, y in self.items() if "cmnd" in dir(y)]

    def values(self): return [y for x, y in self.items() if "cmnd" in dir(y)]


#### C O M M E N T  -=-  S E C T I O N

""" please write comments on changes you made below, so we can get log of things added/changed. """

## BHJTW 27-11-2012 initial import 
