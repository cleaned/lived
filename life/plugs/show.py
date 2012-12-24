# life/plugs/show.py
#
#

""" show stuff. """

def show(event):
    from life import kernel
    if not event.rest: res = kernel.keys()
    else:
        try: res = kernel[event.rest].keys()
        except KeyError: event.reply("nope") ; return
        except AttributeError: event.reply(str(kernel[event.rest])) ; return
    event.reply("%s is %s" % (event.rest or "kernel", ", ".join(res)))

show.cmnd = "show"
show.perms = ["OPER", ]
