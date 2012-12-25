# life/console.py
#
# life monitoring software

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)

"""

## life imports

from life import defines, O, get_kernel
from life.errors import NoCommand, TryAgain, NoAttribute, LifeError
from life.utils import touch, error, completer
from life.defines import datefmt, BLUE, RED, GREEN, BLA, BOLD, YELLOW, ENDC

## basic imports

import readline
import logging
import time
import code
import sys
import os

## alias

j = os.path.join

## bot handling the console

class Console(O):

    """ the console bot doing the input/output. IRC and XMPP soon to follow. """

    completions = {}

    def __init__(self, *args, **kwargs):
        O.__init__(self, *args, **kwargs)
        
    def _raw(self, txt):
        """ output stuff on the screen. """
        try: sys.stdout.write(txt +"\n")
        except TypeError: sys.stdout.write(str(txt))

    def exit(self, *args, **kwargs):
        """ shutdown this bot. """
        self.stopped = True
        logging.warn("writing to history file")
        try: readline.write_history_file(self.hfile)
        except: error()

    def run(self):
        """ start this bot. this function does not return until KeyboardInterrupt """
        kernel = get_kernel()
        kernel.boot()
        if kernel.run_args and not "start" in kernel.run_args: kernel.handle_args() ; return
        if not kernel.silent: print("commands are: %s\n" % ", ".join(kernel.cmnd.keys()))
        try:
            readline.set_completer(completer)
            readline.parse_and_bind("tab: complete")
            self.hfile = j(kernel.root, "run", "history")
            if not os.path.isfile(self.hfile): utils.touch(self.hfile)
            if hasattr(readline, "read_history_file"): readline.read_history_file(self.hfile)
        except: logging.error("no readline")
        self.stopped = False
        kernel.bot.register("bot", "console", self)
        while not self.stopped: 
            try: 
                intxt = input("%s -=- %s%s<%s " % (time.strftime(datefmt), BOLD, YELLOW, ENDC))
                if not intxt: continue
                if self.stopped: return
                event = O(bot=self, origin="shell", channel=kernel.shelluser, input=intxt, cbtype="console")
                event.prepare()
                e = kernel.put(event)
                e.wait()
            except TryAgain: continue
            except NoCommand as ex: self._raw("no %s command available\n" % str(ex))
            except (KeyboardInterrupt, EOFError): break
            except: error()

    def say(self, channel, txt, *args, **kwargs):
        self._raw("%s -=- %s%s>%s %s" % (time.strftime(datefmt), BOLD, RED, ENDC, txt))

