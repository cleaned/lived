# plugs/start.py
#
#

""" start bots. """

## life imports 

from life import O

## basic imports

import logging

## start command

def start(event, *args, **kwargs):
    from life import kernel
    event.untildone = True
    try: btype, server, channel = event.args
    except ValueError: event.reply("<btype> <server> <channel>") ; return
    kwargs["channel"] = channel
    kwargs["server"] = server
    logging.warn("start %s bot (%s)" % (btype, str(kwargs)))
    bot = None
    if btype == "irc":
        from life.irc import IRC
        bot = IRC(**kwargs)
    if not bot: event.reply("cannot make a %s type bot" % btype) ; return
    kernel.bot.register("bot", btype, bot)
    task = O()
    task.want_dispatch = True
    task.do_exec = bot.run
    kernel.put(task)
    bot.status.connected.wait()
    event.done()
    
start.cmnd = start
start.perms = ["OPER", ]
start.threaded = True


