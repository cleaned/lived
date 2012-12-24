# life.py
#
# life monitoring software

"""

    W E L C O M E  T O  L I F E !!!

    -=-

"""

## life imports

from life import defines

## basic imports

import logging
import os
import re

## runtime logging variables

logfilter = ["looponce", "PING", "PONG"]
logplugs = []

## define our own formatter 

class Formatter(logging.Formatter):

    """ hooks into the logging system. """

    notxt = ["B O O T", "R E A D Y", "S H U T D O W N", "error detected"]

    def format(self, record):
        if "__init__" in record.pathname: record.module = record.pathname.split(os.sep)[-2] + ".init"
        target = record.msg
        go = True
        if target[0] in [">", ]: target = "%s%s%s%s" % (defines.RED, target[0], defines.ENDC, target[1:])
        elif target[0] in ["<", ]: target = "%s%s%s%s" % (defines.GREEN, target[0], defines.ENDC, target[1:])
        else: target = "%s%s%s %s" % (defines.GREEN, "!", defines.ENDC, target)
        for no in self.notxt:
            if no in target: record.message = "%s" % target ; go = False
        record.msg = "%s" % target 
        logging.Formatter.format(self, record)
        if not go and target == " ": go = False
        formatdict = {"message": target, "asctime": record.asctime }
        if not go: return defines.format_small % formatdict
        return logging.Formatter.format(self, record)

## MyFilter class

class Filter(logging.Filter):

    def filter(self, record):
        for f in logfilter:
            if f in record.msg: return False
        for modname in logplugs:
            if modname in record.module: record.levelno = logging.WARN ; return True
        return True


## provide a factory function returning a logger ready for use

def log_config(loglevel):
    """ return a properly (for L I F E) configured logger. """
    logger = logging.getLogger("")
    formatter = Formatter(defines.format, datefmt=defines.datefmt)
    formatter_short = Formatter(defines.format_small, datefmt=defines.datefmt)
    level = defines.LEVELS.get(str(loglevel).lower(), logging.NOTSET)
    filehandler = None
    logger.setLevel(level)
    if logger.handlers:
        for handler in logger.handlers: logger.removeHandler(handler)
    try: filehandler = logging.handlers.TimedRotatingFileHandler(j(datadir, "logs", "live.log"), 'midnight')
    except: pass
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if level < logging.WARNING: ch.setFormatter(formatter)
    else: ch.setFormatter(formatter_short)
    ch.addFilter(Filter())
    logger.addHandler(ch)
    if filehandler:
        filehandler.setLevel(level)
        logger.addHandler(filehandler)
    return logger
