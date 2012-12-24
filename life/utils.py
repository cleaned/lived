# life/utils.py
#
# life monitoring software

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)


"""

## life imports

import life
import life.templates
from life import defines, mj, __version__
from life.defines import regular, otypes

## basic imports

import traceback
import optparse
import logging
import socket
import base64
import time
import sys
import re
import os

## alias

j = os.path.join

## notskip function

def notskip(item): return not item.startswith("_")

## resolve_ip function

def resolve_ip(hostname=None, timeout=1.0):
    """ determine the ip address we are running on, we use this for creatin an id. """
    oldtimeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try: ip = socket.gethostbyname(hostname or socket.gethostname())
    except socket.timeout: ip = None
    socket.setdefaulttimeout(oldtimeout)
    return ip

## make_opts

def make_opts():
    """ create commandline parser options. """
    parser = optparse.OptionParser(usage='usage: %prog [options]', version=get_version())
    for option in defines.options:
        type, default, dest, help = option[2:]
        if "store" in type:
            try: parser.add_option(option[0], option[1], action=type, default=default, dest=dest, help=help)
            except Exception as ex: logging.error("error: %s - option: %s" % (str(ex), option)) ; continue 
        else:
            try: parser.add_option(option[0], option[1], type=type, default=default, dest=dest, help=help)
            except Exception as ex: logging.error("error: %s - option: %s" % (str(ex), option)) ; continue 
    return parser.parse_args() # returns (opts, args)
   
## touch function

def touch(fname):
    """ touch a file into existence. """
    try:
        fd = os.open(fname, os.O_RDONLY | os.O_CREAT)
        os.close(fd)
    except: error()

## check_permission function

def check_permissions(ddir, dirmask=defines.dirmask, filemask=defines.filemask):
    """ set permissions of the given "ddir" directory name to utils.filemask/dirmask. """
    uid = os.getuid()
    gid = os.getgid()
    try: stat = os.stat(ddir)
    except OSError: make_dir(ddir) ; stat = os.stat(ddir) 
    if stat.st_uid != uid: os.chown(ddir, uid, gid)
    if os.path.isfile(ddir): mask = filemask
    else: mask = dirmask
    if stat.st_mode != mask: os.chmod(ddir, mask)

## make_dir function

def make_dir(d):
    d = d + os.sep
    target = os.sep
    got = False
    for item in d.split(os.sep):
        if not item: continue
        target = j(target, item, "")
        if not os.path.exists(target): os.mkdir(target) ; got = True
    return got

## make_datadir function

def make_datadir(ddir):
    """ initialise the most important variable in L I F E, the datadir (where the data "lives"). """
    check_permissions(ddir)
    todo = otypes + ["run", "log", "plugs", "default"]
    for t in todo:
        go = j(ddir, t, "")
        try: check_permissions(go)
        except OSError: os.mkdir(go)
        if t in ["plugs", ]:
            ini = j(go, "__init__.py")
            touch(ini)
    histfile = j(ddir, "run", "history")
    if not os.path.isfile(histfile):
        touch(histfile)

## make_plugin function

def make_plugin(ddir):
    """ write a default plugin to disk. for now just to test. see written text below. """
    from .templates import headertxt, plugtxt
    f = open(j(ddir, "plugs", "testing.py"), "w")
    f.write(headertxt % (life.__version__, j(ddir, "plugs", "testing.py"), "plugin", time.ctime(time.time())))
    f.write("\n\n")
    f.write(plugtxt)
    f.close()

## search function

def get_where(search=""):
    """ search the callstack for a certain txt. """
    for loc in callstack():
        if search in loc: return loc

## dump_frame function

def dump_frame(search="code"):
    from life import O
    result = O()
    frame = sys._getframe(1)
    for i in dir(frame):
        if search in i:
            target = getattr(frame, i)
            for j in dir(target):
                result[j] = getattr(target, j)
    return result

## callstack function

def callstack(want=""):
    """ walk the callstack until string is found. stop when toplevel life package is found. """
    result = []
    loopframe = sys._getframe(2)
    if not loopframe: return result
    marker = ""
    while 1:
        try: back = loopframe.f_back
        except AttributeError: break
        codename = get_name(back.f_code)
        filename = back.f_code.co_filename
        mod = []
        for i in filename.split(os.sep)[::-1]:
            if "__init__" in i: continue
            if i.endswith(".py"): i = i[:-3]
            mod.append(i)
            if i in ["life",]: break
        modstr = ".".join(mod[::-1])
        try: lineno = back.f_lineno
        except AttributeError: lineno = "-1"
        result.append("%s.%s:%s" % (modstr, codename, lineno))
        if want in modstr: break
        try: loopframe = back.f_back
        except AttributeError: break
    del loopframe
    return result

## get_name function

def get_name(obj):
    """ return the name of method/function/object or class. used RE are in defines. """
    obj_name = str(obj)
    for name, regex in regular.items():
        target = re.search(regex, obj_name)
        if target: return "%s.%s" % (name, target.group(1))
    return obj_name

## exceptionmsg function

def exceptionmsg(*args, **kwargs):
    """ make a shorter exception message (all on 1 line). """
    exctype, excvalue, tb = sys.exc_info()
    trace = traceback.extract_tb(tb)
    result = ""
    for i in trace:
        fname = i[0]
        linenr = i[1]
        func = i[2]  
        plugfile = fname[:-3].split(os.sep)
        mod = []
        for i in plugfile[::-1]: mod.append(i)
        if i in ["life", ]: break
        ownname = '.'.join(mod[::-1])
        result += "%s:%s %s | " % (ownname, linenr, func)
    del trace
    return "%s%s: %s" % (result, exctype, excvalue)

## shutdown funtion

def shutdown():
    """ shutdown L I F E. """
    from life import get_kernel
    kernel = get_kernel()
    try: kernel.shutdown()
    except: error()
    try: os.remove('life.pid')
    except: pass
    if not kernel.run_args: sys.stdout.write("\n")
    sys.stdout.flush()
    time.sleep(0.1)
    os._exit(0)

## make_pid function

def make_pid():
    """ create the pid file. """
    try: k = open(j(datadir, "run", 'life.pid'),'w') ; k.write(str(os.getpid())) ; k.close()
    except IOError: error()

## get_version function

def get_version():
    """ version string. """
    return "L I F E  -=-  P R O T O T Y P E  %s" % life.__version__

## hello function

def hello():
    """ print welcome message. """
    print(get_version())

## error function

def error(*args, **kwargs):
    """ handle an exception, for now just log the exception in a homemade shorter version. """
    msg = exceptionmsg()
    logging.error("error detected:\n\n%s\n" % msg)
    return msg

## stripbadchar function

def stripbadchar(s):
    """ remove bad characters, where the oridinal is lower then 31, from the string. """
    return "".join([c for c in s if ord(c) >= 31 or c in allowedchars])

## enc_needed function

def enc_needed(s):
    """ check if encoding the filename (end of path) needs to be encoded. """
    return [c for c in s if c not in defines.allowedchars]

## enc_name function

def enc_name(input):
    """ encode a string if string contains bad characters. """
    return str(base64.urlsafe_b64encode(bytes(input, "utf-8")), "utf-8")

## get_source function

def get_source(mod):
    """ return the directory a module is coming from. """
    if not os.getcwd() in sys.path: sys.path.insert(0, os.getcwd())
    source = None
    splitted = mod.split(".")
    if len(splitted) == 1: splitted.append("")
    thedir, file = os.path.split(mod.replace(".", os.sep))
    if os.path.isdir(thedir): source = thedir
    if source and os.path.exists(source): logging.info("source is %s" % source) ; return source
    if not source:
        try: import pkg_resources
        except (ImportError, ValueError): import life.contrib.pkg_resources
        source = p.resource_filename()
    logging.info("source is %s" % source)
    return source

## split_txt function - make portions 

def split_txt(what, l=375):
    """ split output into seperate chunks. """
    txtlist = []
    start = 0
    end = l
    length = len(what)
    for i in range(int(length/end+1)):
        starttag = what.find("</", end)
        if starttag != -1: endword = what.find('>', end) + 1
        else:
            endword = what.find(' ', end)
            if endword == -1: endword = length
        res = what[start:endword]
        if res: txtlist.append(res)
        start = endword
        end = start + l
    return txtlist

## lock_dec function

def lock_dec(lock):
    """ locking decorator. """
    def locked(func):
        """ locking function """
        def lockedfunc(*args, **kwargs):
            """ the locked function. """
            lock.acquire()
            try: return func(*args, **kwargs)
            finally: lock.release()

        return lockedfunc

    return locked

## completa function

completions = {}

def completer(text, state):
    from life import get_kernel
    kernel = get_kernel()
    try: matches = completions[text]
    except KeyError: matches = [value for value in kernel.cmnd.keys() if value.startswith(text)]
    try: return matches[state]
    except: return None
