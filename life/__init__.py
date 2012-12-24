# life/__init__.py
#
#

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)

"""

## L I F E  version

__version__ = 5

import os

## alias

j = os.path.join

## mj function - module joins

def mj(*args): return j(*args).replace(os.sep, ".")

## life imports

from .utils import make_plugin, resolve_ip, make_datadir, notskip, hello, get_name, enc_needed, enc_name, error, get_where
from .errors import NoFileName, NoArgument, NoAttribute, NotSameType, OverloadError, RatherNot, NoTask, NoFunc
from .errors import NoCommand, Denied, UnknownType, NoExec, NoInput, TryAgain, NotImplemented, WrongOType
from .templates import headertxt
from .defines import jsontypes, otypes, bottypes

## basic imports 

import threading
import getpass
import logging
import hashlib
import fcntl
import types
import errno
import uuid
import json
import time
import sys
import os

## basics

ip = resolve_ip()
shelluser = getpass.getuser()
kernel = None

## Big O

class O(dict):

    """ basic class providing dotted access to a dict and json dump. """

    ## basic methods 

    def __init__(self, *args, **kwargs):
        dict.__init__(self, **kwargs)
        if type(self) not in jsontypes: jsontypes.append(type(self))

    def __repr__(self):
        cbt = self.__class__.__name__ 
        ocb = self.__class__.__module__
        return '%s.%s' % (ocb, cbt)

    def __getattr__(self, name):
        try: return self[name]
        except KeyError: self.init(name)
        try: return self[name]
        except KeyError: raise AttributeError(name)

    def __setattr__(self, name, value):
        """ set an attribute, check if no method is overridden and if same types get assigned (string can be overridden). """
        t = type(value)
        if name in self and t == types.MethodType: raise OverloadError(name)
        if t != "" and name in self and type(value) != t: raise NotSameType(name)
        self[name] = value
        return self

    def __call__(self, *args, **kwargs): raise NotImplemented()

    def __exists__(self, a):
        try: self[a] ; return True
        except KeyError: False

    ## O based construction and default attributes

    def init(self, name, *args, **kwargs):
        if name not in self:
            if name in otypes: self[name] = O() 
            if name == "channel": self[name] = ""
            if name == "chan": self[name]["cc"] = ";"
            if name == "ready": self[name] = threading.Event()
            if name == "uuid": self[name] = str(uuid.uuid4())
        return self

    ## calculate the location of this object

    def get_path(self):
        """ make the path of this file. encode the file part if badchars are encountered. """
        if not "filename" in self: self.filename = self.get_id()
        kernel = get_kernel()
        try: head, fn = os.path.split(os.path.abspath(j(kernel.root, self.filename)))
        except AttributeError: raise NoFileName(self.filename)
        if not fn: return head 
        from .utils import make_dir
        make_dir(head)       
        if enc_needed(fn): fn = enc_name(fn)
        return j(head, fn)

    ## calculate the object id

    def get_id(self):
        if "cbtype" not in self: self.cbtype = "default"
        if "otype" not in self: self.otype = "event"
        return "%s%s%s-%s-%s" % (self.otype, os.sep, self.uuid, repr(self), time.time())

    ## output methods

    def direct(self, txt):
        self.bot._raw(txt)

    def reply(self, txt, *args, **kwargs):
        """ add a txt string to the result attribute. this attribute gets returned when ready. use wait() for that. """
        res = O(**self)
        res.otype = "reply"
        res.txt = txt
        res.channel = self.channel
        self.result[str(time.ctime(time.time()))] = res

    def display(self, txt="", target=None):
        """ display results via self._bot """
        for key, item in self.result.items():
            if not target:
                target = self.say
                target(item.channel, item.txt)
            else: target(item.txt)
        self.save_as("display")

    def say(self, *args, **kwargs):
        self.bot.say(*args, **kwargs)

    ## wait for results

    def wait(self, sec=3.0):
        """ wait for the results to show up. """
        logging.info("waiting %s seconds" % sec)
        self.prepare()
        self.ready.wait(sec)
        if not self.result: raise TryAgain()
        return self

    ## JSON display functions 


    def full(self, *args, **kwargs):
        """ convert the current object (dict) to json string, replacing non convertable data to it's string representation (utils.get_name). """
        return json.dumps(self, default=utils.get_name, *args, **kwargs)

    def json(self, *args, **kwargs):
        """ convert the current object (dict) to json string, replacing non convertable data to it's string representation (utils.get_name). """
        return json.dumps(self.strip(["bot", "result", "status", "kernel"], "_"), default=utils.get_name, *args, **kwargs)

    ## Persist functionality - reading from and saving to disk

    def from_file(self, filename):
        from life.persist import Persist
        kernel = get_kernel()
        input = Persist().load(j(kernel.root, filename))
        self.update(input)        

    def read(self, *args, **kwargs):
        """ read the JSON from file, skipping comments (lines starting with #). """
        try: f = open(self.get_path(), "r")
        except IOError as ex:
            if ex.errno == errno.ENOENT: return "{}"
            raise
        res = ""
        for line in f.readlines():
            if not line.strip().startswith("#"): res += line
        if not res.strip(): return "{}"
        f.close()
        return res

    def load(self, filename, verify=False, *args, **kwargs):
        """ convert the data on disk (a JSON dict) to this object. """
        logging.warn("load %s" % filename)
        self.filename = filename
        ondisk = self.read()
        self.prepare()
        fromdisk = O(**json.loads(ondisk))
        if "data" in fromdisk: result = O(**fromdisk.data)
        else: result = O(**fromdisk)
        if verify and fromdisk.signature:
            if self.make_signature(result) != fromdisk.signature: raise SignatureError(self.filename)
        self.update(result)
        return self

    def save_as(self, otype):
        self.otype = otype
        self.save()

    def save(self, *args, **kwargs):
        """ save current data to disk, using a container to hold meta data (signature etc.). """
        path = self.get_path()
        if not path: raise NoFileName()
        todisk = O(**self)
        if "config" in path: type = "config"
        elif "plugs" in path: type = "plugin"
        else: type = "data"
        todisk.wtime = time.time()
        todisk.signature = self.make_signature()
        try: result = todisk.full(indent=True)
        except TypeError: raise NoJSON(self.filename)
        logging.warn("save %s" % self.filename)
        datafile = open(path + ".tmp", 'w')
        fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        datafile.write(headertxt % (__version__, self.filename, type, time.ctime(todisk.wtime)))
        datafile.write(result)
        datafile.write("\n")
        fcntl.flock(datafile, fcntl.LOCK_UN)
        datafile.close()
        os.rename(path + ".tmp", path)

    ## register methods - adding objects to a list in the O object

    def get_regged(self, otype):
        try: return [(x, y) for x, y in self[otype].items() if type(y) == list]
        except KeyError as ex: logging.warn("no regged %s in %s" % (otype, self.json())) ; return []

    def get_reg(self, otype, name):
        try: return self[otype][name]
        except: return []

    def register(self, *args, **kwargs):
        """ add an O to this one. """   
        if len(args) != 3: raise NoArgument()
        otype = args[0]
        name = args[1] 
        item = args[2] 
        if "name" in self: sname = self.name
        else: sname = get_name(self)
        logging.warn("register %s.%s in %s" % (otype, name, sname))
        if name not in self: self[name] = []
        if item not in self[name]: self[name].append(item)
        return self

    ## power core dispatching stuff - running code on the O data

    def run_cb(self, *args, **kwargs):
        if args: target = args[0]
        else: target = self
        for callback in self.get_reg("cb", target.cbtype):
            logging.info("cb %s - %s" % (target.cbtype, str(callback)))
            try: pre = getattr(callback, "pre")
            except AttributeError: self.status[str(time.ctime(time.time()))] = "no pre" ; pre = None ; self.do_status = True
            if pre and not pre(target): logging.debug("pre failed") ; continue
            self.status[str(time.ctime(time.time()))] = callback(target)
            try: post = callback.post
            except AttributeError: self.status[str(time.ctime(time.time()))] = "no post" ; self.do_status = True ; continue
            post(target)
        target.resolved = "cb"
        return target

    def dispatch(self, *args, **kwargs):
        if args: target = args[0]
        else: target = self
        kernel = get_kernel()
        logging.debug("target %s" % str(target))
        if target.hascc():
            target.want_dispatch = True
            logging.info("dispatch %s" % target.cmnd)
            commands = kernel.get_reg("cmnd", target.cmnd)
            for command in commands:
                try: pre_func = getattr(command, "pre")
                except AttributeError: pre_func = None 
                if pre_func and not pre_func(target): logging.info("pre failed") ; return
                status = command(target)
                self.status[str(time.ctime(time.time()))] = status or "ok"
                try: post_func = getattr(command, "post")
                except AttributeError: post_func = None  
                if post_func: post_func(target)
        target.resolved = "cmnd"
        return target

    def execute(self, *args, **kwargs):
        if args: target = args[0]
        else: target = self
        try: func = getattr(target, "do_exec")
        except (AttributeError, NoAttribute): func = None
        if not func: raise NoFunc() 
        try: pre_func = getattr(func, "pre")
        except AttributeError: pre_func = None 
        if pre_func and not pre_func(target): logging.info("pre failed") ; return
        status = func(target)
        self.status[str(time.ctime(time.time()))] = status or "ok"
        try: post_func = getattr(func, "post")
        except AttributeError: post_func = None  
        if post_func: post_func(target)
        target.resolved = "thread"
        target.done()
        return target

    ## helper methods

    def prepare(self):
        if "txt" not in self: self.parse()
        if "txt" in self:
            try:
                if self.hascc(): self.cmnd = self.txt.split()[0][1:]
                self.args = self.txt.split()[1:]
                self.rest = " ".join(self.args)
            except ValueError: self.args = [] ; self.rest = ""
        return self

    def copyin(self, input):
        """ copy in a dict. """
        target = O(**input)
        self.update(target)

    def strip(self, ignore=[], ignorestart=""):
        """ remove attributes starting with _ """
        return { k: self[k] for k in self if not k[0] in ignorestart and not k in ignore }

    def make_signature(self, sig=None):
        """ create a signature of current data, so we can ensure originality when needed. """
        return str(hashlib.sha1(bytes(str(sig or self), "utf-8")).hexdigest())

    def hascc(self, input=None):
        """ check if event.txt begins with a control character (cc). indicates a command given. """
        if not input: input = self.txt
        return input[0] in self.chan.cc

    def done(self):
        """ signal when the event is processed. """
        self.ready.set() 

    def iters(self):
        for item in self.values():
            try: item.__iter__ ; yield item
            except AttributeError: continue

    def parse(self, *args, **kwargs):
        if "input" in self: self.txt = ";%s" % self.input

## boot life

def get_kernel():
    global kernel
    if not kernel:
        from .runtime import RunTime
        kernel = RunTime(name="kernel")
    return kernel

kernel = get_kernel()

#### C O M M E N T  -=-  S E C T I O N

""" please write comments on changes you made below, so we can get log of things added/changed. """

## BHJTW 27-11-2012 initial import 
