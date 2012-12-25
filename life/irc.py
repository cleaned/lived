# life/irc.py
#
#
# http://www.irchelp.org/irchelp/rfc/rfc2812.txt

""" an ircevent is extracted from the IRC string received from the server. """

## life imports

from life import kernel, O

from .utils import error, stripbadchar, split_txt, lock_dec
from .errors import RemoteDisconnect, NoInput
from .defines import regular, YELLOW, ENDC, RED, BLA

## basic imports

import logging
import socket
import time 
import re 
import types 
import copy
import _thread
import threading

## defines

cpy = copy.deepcopy

## locks

outlock = _thread.allocate_lock()
outlocked = lock_dec(outlock)

## IRCEvent class

class IRCEvent(O):

    """ represents an IRC event. """

    def __init__(self, *args, **kwargs):
        O.__init__(self, *args, **kwargs)
        self.parse()
        
    def parse(self):
        """ parse raw string into ircevent. """
        if not self.input: raise NoInput()
        rawstr = self.input
        self.servermsg = False
        splitted = re.split('\s+', rawstr)
        if not rawstr[0] == ':': self.servermsg = True
        self.prefix = splitted[0]
        if self.servermsg: self.cbtype = self.prefix
        else: self.cbtype = splitted[1]
        try: 
            nickuser = self.prefix.split('!')
            self.origin = nickuser[1]
            self.nick = nickuser[0][1:]
        except IndexError: self.origin = self.prefix ; self.servermsg = True
        if self.cbtype in pfc:
            self.arguments = splitted[2:pfc[self.cbtype]+2]
            txtsplit = re.split('\s+', rawstr, pfc[self.cbtype]+2)
            self.txt = txtsplit[-1]
        else:
            logging.debug("cmnd not in pfc - %s" % rawstr)
            self.arguments = splitted[2:]
        if self.arguments: self.target = self.arguments[0]
        self.postfix = ' '.join(self.arguments)
        if not "txt" in self: self.txt = rawstr.rsplit(":")[-1]
        if self.txt.startswith(":"): self.txt = self.txt[1:]
        if not "channel" in self:
            for c in self.arguments + [self.txt, ]:
                if c.startswith("#"): self.channel = c
        if self.servermsg: 
            self.origin = self.origin[1:-1]
            self.channel = self.origin 
        if not "origin" in self: self.origin = self.channel
        if not "target" in self: self.target = self.channel or self.origin
        return self

## IRCBot class

class IRC(O):

    """ the irc class, provides interface to irc related stuff. """

    marker = "\r\n"

    def __init__(self, *args, **kwargs):
        O.__init__(self, *args, **kwargs)
        if "name" not in self.cfg: self.cfg.name = "default-irc"
        if "username" not in self.cfg: self.cfg.username = "default-irc"
        if "nick" not in self.cfg: self.cfg.nick = "lijf"
        if "ipv6" not in self.cfg: self.cfg.ipv6 = False
        if "server" in kwargs: self.cfg.server = kwargs["server"]
        if "server" not in self.cfg: self.cfg.server = "localhost"
        if "port" not in self.cfg: self.cfg.port = 6667
        if "ssl" not in self.cfg: self.cfg.ssl = False
        if "channels" not in self.cfg: self.cfg.channels = []
        if "channel" in kwargs: self.cfg.channels.append(kwargs["channel"])
        if "encoding" not in self: self.cfg.encoding = "utf-8"
        self.status.connected = threading.Event()
        self.cb = O(name="cb")
        self.cb.register("cb", "250", self._onconnect)
        self.cb.register("cb", "PING", self.pong)
        self._lock = _thread.allocate_lock()

    def _raw(self, txt):
        """ send raw text to the server. """
        logging.warn("> %s" % txt)
        if not txt.endswith(self.marker): txt += self.marker
        itxt = bytes(txt, self.cfg.encoding)
        if 'ssl' in self.cfg and self.cfg.ssl: self.sock.write(itxt)
        else: self.sock.send(itxt[:502])

    @outlocked
    def send(self, txt):
        """ send txt over the wire and sleep 3 seconds to avoid excess flood. """
        if not txt or self.stopped or not self.sock: return 0
        try:
            self.lastoutput = time.time()
            self._raw(self.normalize(txt))
        except Exception as ex: error() ; return False
        time.sleep(3)
        return True

    def _connect(self):
        """ connect to server/port using nick. """
        self.stopped = False
        if self.cfg.ipv6: self.oldsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else: self.oldsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = self.bind()
        logging.warn('connect %s - %s (%s)' % (server, self.cfg.port, self.cfg.name))
        self.oldsock.settimeout(60)
        self.oldsock.connect((server, int(str(self.cfg.port))))	
        self.blocking = 1
        self.oldsock.setblocking(self.blocking)
        logging.warn('connection made to %s (%s)' % (server, self.cfg.name))
        self.fsock = self.oldsock.makefile("r")
        if self.blocking:
            socktimeout = 301.0
            self.oldsock.settimeout(socktimeout)
        if 'ssl' in self.cfg and self.cfg['ssl']: self.sock = socket.ssl(self.oldsock) 
        else: self.sock = self.oldsock
        self.connecttime = time.time()
        return True

    def _onconnect(self, *args, **kwargs):
        """ overload this to run after connect. """
  
        logging.warn("logged on !!")
        if "onconnect" in self.cfg: time.sleep(2) ; self._raw(self.cfg.onconnect)
        if "servermodes" in self.cfg: self._raw("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
        self.join_channels(*args, **kwargs)
        self.status.connected.set()

    def bind(self):
        server = self.cfg.server
        try: self.oldsock.bind((server, 0))
        except socket.error:
            if not server:
                try: socket.inet_pton(socket.AF_INET6, self.cfg.server)
                except socket.error: pass
                else: server = self.cfg.server
            if not server:  
                try: socket.inet_pton(socket.AF_INET, self.cfg.server)
                except socket.error: pass
                else: server = self.cfg.server
            if not server:
                ips = []
                try:
                    for item in socket.getaddrinfo(self.cfg.server, None):
                        if item[0] in [socket.AF_INET, socket.AF_INET6] and item[1] == socket.SOCK_STREAM:
                            ip = item[4][0]
                            if ip not in ips: ips.append(ip)
                except socket.error: pass
                else: server = random.choice(ips)
        return server

    def handle_one(self, line):
        """ loop on the socketfile. """
        e = IRCEvent(bot=self, input=line)
        e.prepare()
        kernel.put(e)
        return e

    def logon(self):
        """ log on to the network. """
        if "password" in self.cfg: self._raw("PASS %s" % self.cfg.password)
        logging.warn('logging in on %s - this may take a while' % self.cfg.server)
        if "username" in self.cfg: username = self.cfg.username
        else: username =  "lijf"
        if "realname" in self.cfg: realname = self.cfg.realname
        else: realname = "lijf"
        self._raw("NICK %s" % self.cfg.nick)
        self._raw("USER %s localhost %s :%s" % (username, self.cfg.server, realname))

    def say(self, channel, txt):
        txt = self.normalize(txt)
        for line in split_txt(txt):
            self.send("PRIVMSG %s :%s" % (channel, line.strip()))

    def join_channels(self, *args, **kwargs):
        for channel in self.cfg.channels: self.join(channel)

    def broadcast(self, txt):
        """ broadcast txt to all joined channels. """
        for i in self.cfg.channels:
            self.say(i, txt)

    def connect(self, reconnect=True):
        """ 
            connect to server/port using nick .. connect can timeout so catch
            exception .. reconnect if enabled.
        """
        res = self._connect()
        if res: time.sleep(1) ; self.logon()
        return res

    def run(self, *args, **kwargs):
        logging.warn("run %s" % self.cfg.server)
        if not self.connect(): raise NoConnection(self.cfg.server)
        lastline = ""
        self.stopped = False
        while not self.stopped:
             if "ssl" in self.cfg and self.cfg.ssl: inbytes = self.sock.read()
             else: inbytes = self.sock.recv(512)
             intxt = str(inbytes, self.cfg.encoding)
             if intxt == "": raise RemoteDisconnect()
             if not intxt.endswith(self.marker): lastline += intxt ; continue
             txt = lastline + intxt
             for line in txt.split(self.marker):
                 if not line: continue
                 logging.warn("< %s" % line)
                 self.handle_one(line)
             lastline = ""

    def close(self):
        """ close the connection. """
        if 'ssl' in self.cfg and self.cfg['ssl']: self.oldsock.shutdown(2)
        else: self.sock.shutdown(2)
        if 'ssl' in self.cfg and self.cfg['ssl']: self.oldsock.close()
        else: self.sock.close()
        self.fsock.close()

    def handle_pong(self, event):
        """ set pongcheck on received pong. """
        self.pongcheck = True

    def donick(self, nick, setorig=False, save=False, whois=False):
        """ change nick .. optionally set original nick and/or save to config.  """
        nick = nick[:16]
        self.send('NICK %s\n' % nick)

    def join(self, channel, password=None):
        """ join channel with optional password. """
        if password: self._raw('JOIN %s %s' % (channel, password))
        else: self.send('JOIN %s' % channel)

    def part(self, channel):
        """ leave channel. """
        self.send('PART %s' % channel)
        if channel in self.cfg.channels: self.cfg.channels.remove(channel) ; self.cfg.save()

    def who(self, who):
        """ send who query. """
        self.send('WHO %s' % who.strip())

    def names(self, channel):
        """ send names query. """
        self.send('NAMES %s' % channel)

    def whois(self, who):
        """ send whois query. """
        self.send('WHOIS %s' % who)

    def privmsg(self, printto, what):
        """ send privmsg to irc server. """
        self.send('PRIVMSG %s :%s' % (printto, what))

    def voice(self, channel, who):
        """ give voice. """
        self.send('MODE %s +v %s' % (channel, who))
 
    def doop(self, channel, who):
        """ give ops. """
        self.send('MODE %s +o %s' % (channel, who))

    def delop(self, channel, who):
        """ de-op user. """
        self.send('MODE %s -o %s' % (channel, who))

    def quit(self, reason='http://github.com/feedbackflow/life'):
        """ send quit message. """
        self.send('QUIT :%s' % reason)

    def notice(self, printto, what):
        """ send notice. """
        self.send('NOTICE %s :%s' % (printto, what))
 
    def ctcp(self, printto, what):
        """ send ctcp privmsg. """
        self.send("PRIVMSG %s :\001%s\001" % (printto, what))

    def ctcpreply(self, printto, what):
        """ send ctcp notice. """
        self.send("NOTICE %s :\001%s\001" % (printto, what))

    def action(self, printto, what, event=None, *args, **kwargs):
        """ do action. """
        self.send("PRIVMSG %s :\001ACTION %s\001" % (printto, what))

    def getchannelmode(self, channel):
        """ send MODE request for channel. """
        self.send('MODE %s' % channel)

    def settopic(self, channel, txt):
        """ set topic of channel to txt. """
        self.send('TOPIC %s :%s' % (channel, txt))

    def ping(self, *args, **kwargs):
        """ ping the irc server. """
        try: self.send('PING :%s' % self.cfg.server) ; return True
        except Exception as ex: return False

    def pong(self, *args, **kwargs):
        """ ping the irc server. """
        try: self.send('PONG :%s' % self.cfg.server) ; return True
        except Exception as ex: return False

    def broadcast(self, txt):
        """ broadcast txt to all joined channels. """
        for i in self.cfg.channels: self.say(i, txt)

    def gettopic(self, channel, event=None):
        """ get topic data. """
        q = queue.Queue()
        i332 = waiter.register("332", queue=q)
        i333 = waiter.register("333", queue=q)
        self.putonqueue(7, None, 'TOPIC %s' % channel)
        res = waitforqueue(q, 5000)
        who = what = when = None
        for r in res:
            if not r.postfix: continue
            try:
                if r.cmnd == "332": what = r.txt ; waiter.ready(i332) ; continue
                waiter.ready(i333)
                splitted = r.postfix.split()
                who = splitted[2]
                when = float(splitted[3])
            except (IndexError, ValueError): continue
            return (what, who, when)

    def _dccresume(self, sock, nick, userhost, channel=None):
        """ resume dcc loop. """
        if not nick or not userhost: return
        start_new_thread(self._dccloop, (sock, nick, userhost, channel))

    def _dcclisten(self, nick, userhost, channel):
        """ accept dcc chat requests. """
        try:
            listenip = socket.gethostbyname(socket.gethostname())
            (port, listensock) = getlistensocket(listenip)
            ipip2 = socket.inet_aton(listenip)
            ipip = struct.unpack('>L', ipip2)[0]
            chatmsg = 'DCC CHAT CHAT %s %s' % (ipip, port)
            self.ctcp(nick, chatmsg)
            self.sock = sock = listensock.accept()[0]
        except Exception as ex: error() ; return
        self._dodcc(sock, nick, userhost, channel)

    def _dodcc(self, sock, nick, userhost, channel=None):
        """ send welcome message and loop for dcc commands. """
        try:
            sock.send(bytes('Welcome to the  L I F E  partyline ' + nick + " ;]\n", self.encoding))
            partylist = partyline.list_nicks()
            if partylist: sock.send(bytes("people on the partyline: %s\n" % ' .. '.join(partylist, self.encoding)))
        except Exception as ex: error() ; return
        start_new_thread(self._dccloop, (sock, nick, userhost, channel))

    def _dccloop(self, sock, nick, userhost, channel=None):
        """ loop for dcc commands. """
        sockfile = sock.makefile('r')
        sock.setblocking(True)
        partyline.add_party(self, sock, nick, userhost, channel)
        while 1:
            try:
                res = sockfile.readline()
                if self.stopped or not res: break
                self.handle_one(res)
            except socket.timeout: time.sleep(0.01)
            except socket.error as ex:
                if ex.errno in [EAGAIN, ]: continue
                else: raise
            except Exception as ex: error()
        partyline.del_party(nick)
        sockfile.close()

    def _dccconnect(self, nick, userhost, addr, port):
        """ connect to dcc request from nick. """
        try:
            port = int(port)
            if re.search(':', addr):
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((addr, port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((addr, port))
        except Exception as ex: error() ; return
        self._dodcc(sock, nick, userhost, userhost)

    def normalize(self, what):
        txt = re.sub('\s+', " ", what)
        txt = txt.replace("\n", "")
        txt = stripbadchar(txt)
        txt = txt.replace("<b>", "\002")
        txt = txt.replace("</b>", "\002")
        txt = txt.replace("<i>", "\0032")
        txt = txt.replace("</i>", "\003")
        txt = txt.replace("<li>", "\0033*\003 ")
        txt = txt.replace("</li>", "")
        txt = txt.replace("<br><br>", " - ")
        txt = txt.replace("<br>", " [!] ")
        txt = txt.replace("&lt;b&gt;", "\002")
        txt = txt.replace("&lt;/b&gt;", "\002")
        txt = txt.replace("&lt;i&gt;", "\003")
        txt = txt.replace("&lt;/i&gt;", "")
        txt = txt.replace("&lt;h2&gt;", "\0033")
        txt = txt.replace("&lt;/h2&gt;", "\003")
        txt = txt.replace("&lt;h3&gt;", "\0034")
        txt = txt.replace("&lt;/h3&gt;", "\003")
        txt = txt.replace("&lt;li&gt;", "\0034")
        txt = txt.replace("&lt;/li&gt;", "\003")
        return txt

## postfix count - how many arguments

pfc = {}
pfc['NICK'] = 0
pfc['QUIT'] = 0
pfc['SQUIT'] = 1
pfc['JOIN'] = 0
pfc['PART'] = 1
pfc['TOPIC'] = 1
pfc['KICK'] = 2
pfc['PRIVMSG'] = 1
pfc['NOTICE'] = 1
pfc['SQUERY'] = 1
pfc['PING'] = 0
pfc['ERROR'] = 0
pfc['AWAY'] = 0
pfc['WALLOPS'] = 0
pfc['INVITE'] = 1
pfc['001'] = 1
pfc['002'] = 1
pfc['003'] = 1
pfc['004'] = 4
pfc['005'] = 15
pfc['302'] = 1
pfc['303'] = 1
pfc['301'] = 2
pfc['305'] = 1
pfc['306'] = 1
pfc['311'] = 5
pfc['312'] = 3
pfc['313'] = 2
pfc['317'] = 3
pfc['318'] = 2
pfc['319'] = 2
pfc['314'] = 5
pfc['369'] = 2
pfc['322'] = 3
pfc['323'] = 1
pfc['325'] = 3
pfc['324'] = 4
pfc['331'] = 2
pfc['332'] = 2
pfc['341'] = 3
pfc['342'] = 2
pfc['346'] = 3
pfc['347'] = 2
pfc['348'] = 3
pfc['349'] = 2
pfc['351'] = 3
pfc['352'] = 7
pfc['315'] = 2
pfc['353'] = 3
pfc['366'] = 2
pfc['364'] = 3
pfc['365'] = 2
pfc['367'] = 2
pfc['368'] = 2
pfc['371'] = 1
pfc['374'] = 1
pfc['375'] = 1
pfc['372'] = 1
pfc['376'] = 1
pfc['378'] = 2
pfc['381'] = 1
pfc['382'] = 2
pfc['383'] = 5
pfc['391'] = 2
pfc['392'] = 1
pfc['393'] = 1
pfc['394'] = 1
pfc['395'] = 1
pfc['262'] = 3
pfc['242'] = 1
pfc['235'] = 3
pfc['250'] = 1
pfc['251'] = 1
pfc['252'] = 2
pfc['253'] = 2
pfc['254'] = 2
pfc['255'] = 1
pfc['256'] = 2
pfc['257'] = 1
pfc['258'] = 1
pfc['259'] = 1
pfc['263'] = 2
pfc['265'] = 1
pfc['266'] = 1
pfc['401'] = 2
pfc['402'] = 2
pfc['403'] = 2
pfc['404'] = 2
pfc['405'] = 2
pfc['406'] = 2
pfc['407'] = 2
pfc['408'] = 2
pfc['409'] = 1
pfc['411'] = 1
pfc['412'] = 1
pfc['413'] = 2
pfc['414'] = 2
pfc['415'] = 2
pfc['421'] = 2
pfc['422'] = 1
pfc['423'] = 2
pfc['424'] = 1
pfc['431'] = 1
pfc['432'] = 2
pfc['433'] = 2
pfc['436'] = 2
pfc['437'] = 2
pfc['441'] = 3
pfc['442'] = 2
pfc['443'] = 3
pfc['444'] = 2
pfc['445'] = 1
pfc['446'] = 1
pfc['451'] = 1
pfc['461'] = 2
pfc['462'] = 1
pfc['463'] = 1
pfc['464'] = 1
pfc['465'] = 1
pfc['467'] = 2
pfc['471'] = 2
pfc['472'] = 2
pfc['473'] = 2
pfc['474'] = 2
pfc['475'] = 2
pfc['476'] = 2
pfc['477'] = 2
pfc['478'] = 3
pfc['481'] = 1
pfc['482'] = 2
pfc['483'] = 1
pfc['484'] = 1
pfc['485'] = 1
pfc['491'] = 1
pfc['501'] = 1
pfc['502'] = 1
pfc['700'] = 2
