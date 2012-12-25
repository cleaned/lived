# life/runtime.py
#
#

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)

"""

## life imports

from life import O, j, mj
from life.errors import NoAttribute
from life.utils import get_name, error, make_opts, hello, shutdown

## basic imports

import logging
import getpass
import time
import sys
import os

## Context class - provided context for the whole program

class RunTime(O):

    def __init__(self, *args, **kwargs):
        O.__init__(self, *args, **kwargs)
        if args: ddir = args[0]
        else: ddir = ""
        self.bots = []
        self.datadir = ddir or ".life"
        self.homedir = os.path.expanduser("~")
        self.prepare()
        if not self.datadir in sys.path: sys.path.append(self.root)

    def prepare(self):
        self.root = j(self.homedir, self.datadir)
        self.plugdir = j(self.root, "plugs")
        self.logdir = j(self.root, "logs")

    def shutdown(self):
        if not self.run_args: print(" ")
        for bottype, botlist in self.get_regged("bot"):
            for bot in botlist:
                logging.warn("shutting down %s" % bottype)
                try: exit = getattr(bot, "exit")
                except (AttributeError, TypeError): continue
                exit()
        
    def boot(self):
        """ stuff all the needed stuff in a core object and initialise them.  """
        from .tasks import Dispatcher
        from .plugins import Plugins 
        from .utils import resolve_ip, make_datadir, make_plugin, resolve_host
        from .log import log_config
        opts, args = make_opts()
        if opts.loglevel: loglevel = opts.loglevel
        else: loglevel = "error"
        self.logger = log_config(loglevel)
        if opts.datadir: self.datadir = opts.datadir ; self.prepare()
        self.silent = args and "start" not in args 
        if not self.silent: hello()
        if opts.loglevel: logging.warn("B O O T")
        make_datadir(self.root)
        make_plugin(self.root)
        self.run_opts = opts
        self.run_args = args
        self.ip = resolve_ip()
        self.host = resolve_host()
        self.shelluser = getpass.getuser()
        self.packages = ["life.plugs", mj(self.root, "plugs")]
        self.plugin = Plugins(filename=j("run", "plugins"))
        self.cb = O(name="cb")
        self.cmnd = O(name="cmnd")
        self.bot = O(name="bot")
        self.dispatcher = Dispatcher()
        self.load_all()
        if not args: logging.warn("R E A D Y") ; print(" ")
        return self

    def load_all(self):
        self.cfg.load(j("cfg", "main"))
        self.plugin.load_all()

    def put(self, *args, **kwargs):
        self.dispatcher.put(*args, **kwargs) 
        return args[0]

    def handle_args(self, *args, **kwargs):
        event = O(**kwargs)
        event.cbtype = "console"
        event.txt = ";" + " ".join(self.run_args)
        event.prepare()
        event.want_dispatch = True
        self.dispatch(event)
        event.display(target=sys.stdout.write)
        sys.stdout.write("\n")
        sys.stdout.flush()
        return event

