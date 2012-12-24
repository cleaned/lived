# life/plugs.py
#
# life monitoring software

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)

"""

## life imports

from life import O, kernel

from life.errors import NoCommand, Denied
from life.cmnds import Commands
from life.utils import error, make_dir, get_name

## basic imports

import logging
import types
import time
import imp
import os

## alias

j = os.path.join

## module join 

def mj(*args):
    todo = []
    for arg in args: todo.append(args.replace(os.sep, "."))
    return ".".join(todo)

## plugins to handle all the things happening in life

class Plugins(O):

    """ contains the plugins (imported modules from datadir/plugs) registered with L I F E. """

    def scan(self, module, attr):
        """ scan the imported modules on commands (have a cmnd attribute). """
        logging.info("look %s (%s)" % (get_name(module), attr))
        for name in dir(module):
            obj = getattr(module, name)
            if not obj: continue
            try: thing = getattr(obj, attr)
            except AttributeError: continue
            if type(thing) == list: target = thing
            else: target = [name, ]
            for t in target: kernel[attr].register(attr, t, obj)

    def plugins(self, plugdir):
        """ return all plugins from the datadir/plugs directory. """
        return [x[:-3] for x in os.listdir(plugdir) if x.endswith(".py")]

    def load_all(self, *args, **kwargs):
        """ load all plugins. """
        self.load_dir(kernel.plugdir)
        path, tail = os.path.split(__file__)
        coreplugsdir = j(path, "plugs")
        self.load_dir(coreplugsdir)
        return coreplugsdir

    def load_dir(self, dirname):
        logging.warn("load %s" % dirname)
        for plugname in self.plugins(dirname):
            if "__" in plugname: continue
            try: mod = self.load_mod(plugname, dirname, True)
            except: error() ; continue
            if not mod: continue
            self.scan(mod, "cmnd")
            self.scan(mod, "cb")

    def load_mod(self, plugname, pdir="", force=False):
        """ load a plugin as a module and store it in this object. """
        logging.warn("load plugin.%s" % plugname)
        if plugname in self:
            if not force: return self[plugname]
            self[plugname] = imp.reload(self[plugname])
        else:
            if not pdir: pdir = j(kernel.plugdir)
            search = imp.find_module(plugname, [pdir,])
            mod = imp.load_module(plugname, *search)
            self[plugname] = mod
        return self[plugname]
 
    def unload(self, plugname):
        """ unload a plugin. """
        logging.warn("unload %s" % plugname)
        del self[plugname]

    def reload(self, plugname, force=False):
        """ unload a plugin before loading it. """
        self.unload(plugname)
        mod = self.load_mod(plugname, force)
        self.scan(mod, "cmnd")
        self.scan(mod, "cb")
        return mod


#### C O M M E N T  -=-  S E C T I O N

""" please write comments on changes you made below, so we can get log of things added/changed. """

## BHJTW 27-11-2012 initial import 

