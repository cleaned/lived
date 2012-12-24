# life/defines.py
#
#

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    Attribute codes: 00=none 01=bold 04=underscore 05=blink 07=reverse 08=concealed
    Text color codes: 30=black 31=red 32=green 33=yellow 34=blue 35=magenta 36=cyan 37=white
    Background color codes: 40=black 41=red 42=green 43=yellow 44=blue 45=magenta 46=cyan 47=white

"""

## basic imports

import logging
import string
import re

## static defined stuff

regular = {
    "code": re.compile("code\s+object\s+(\S+)", re.I),
    "meth": re.compile('method\s+(\S+)', re.I),
    "func": re.compile("function\s+(\S+)", re.I),
    "obj": re.compile('<(\S+)\s+object', re.I),
    "cls": re.compile("class\s+'(\S+)'>", re.I),
    "mod": re.compile("module\s+'(\S+)'", re.I),
}

## the defines !!

otypes = ["chan", "bot", "cfg", "task", "user", "cmnd", "cb", "plugin", "event", "basic", "result", "status"]
bottypes = ["xmmp", "irc", "console"]
jsontypes = [bytes, str, float, dict, list, int, bool, None, True, False]

ERASE_LINE = '\033[2K'
BOLD='\033[1m'
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
BLA = '\033[95m'
ENDC = '\033[0m'

re_dcc = re.compile('\001DCC CHAT CHAT (\S+) (\d+)\001', re.I)
dirmask = 0o700
filemask = 0o600
allowedchars = string.ascii_letters + string.digits + "_,-."
datefmt = BLUE + '%H:%M:%S' + ENDC

format = "%(asctime)-8s -=- %(message)-74s -=- (%(module)s.%(funcName)s.%(lineno)s)"
format_small = "%(asctime)-8s -=- %(message)-75s"
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'warn': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
        }

TAGS = {
         'PING': logging.DEBUG,
         '> PONG': logging.DEBUG,
       }

skiptypes = [str, ]

options = [
              ('-a', '--api', 'store_true', False, 'api',  "enable api server"),
              ('', '--apiport', 'string', "", 'apiport', "port on which the api server will run"),
              ('-c', '--channel', 'string', "", 'channel',  "channel to join"),
              ('-d', '--datadir', 'string', "", 'datadir',  "datadir of the bot"),
              ('-l', '--loglevel', 'string', "", 'loglevel',  "loglevel of the bot"),
              ('-r', '--resume', 'string', "", 'doresume', "resume the bot from the folder specified"),
              ('-s', '--server', 'string', "", 'server',  "server to connect to"),
          ]
