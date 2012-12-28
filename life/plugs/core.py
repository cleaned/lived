# life/plugs/core.py
#
#

""" core callbacks. """


def do_dispatch(event):
    from life import kernel
    event.prepare()
    e = kernel.dispatch(event)
    event.display()

do_dispatch.cb = ["PRIVMSG", "CONSOLE"]

