# life/tasks.py
#
# life monitoring software

"""

    W E L C O M E  T O  L I F E !!!

    -=-

    (this code is best enjoyed on a wide screen)

"""

## life imports

from life import O, get_kernel

from life.errors import Stop, NoAttribute, NoTask, NoExec, NoInput
from life.utils import error, exceptionmsg

## basic imports

import collections
import threading
import logging
import random
import types
import time

## TaskRunner class

class TaskRunner(threading.Thread):

    """ A task is a thread looping over a queue, handling jobs putted to it. """

    counter = 1

    def __init__(self, *args, **kwargs):
        self.rtype = str(type(self))
        threading.Thread.__init__(self, None, self._loop, self.rtype, args, kwargs)
        self.queue = collections.deque()
        self.stopped = False
        self.lasttime = 0
        self.setDaemon(True)
        self.counter += 1
        self.running = False

    def _loop(self):
        """ the threadloop, polls on self.queue (a deque) until a job arrives. """
        while not self.stopped:
            try: args, kwargs = self.queue.popleft()
            except IndexError: time.sleep(0.1) ; continue
            try: task = args[0]
            except IndexError: task = None
            if not task: logging.debug("no task %s" % str(args)) ; continue
            if self.stopped: break
            self.running = True
            if "cbtype" in task: logging.warn("task %s" % task.get_id())
            self.counter += 1
            self.lasttime = time.time()
            try: self.handle_task(task)
            except: error()
            task.done()
            self.running = False
        logging.warn("stopping loop")


    def handle_task(self, *args, **kwargs):
        if not args: raise NoTask()
        task = args[0]
        kernel = get_kernel()
        if "do_exec" in task: kernel.execute(task)
        else:
            try: 
                if task.bot: task.bot.run_cb(task)
                kernel.run_cb(task)
                msg = "elapsed %s" % (time.time() - self.lasttime)
            except Exception as ex: msg = error() ; task.do_display = True
        task.status[str(time.ctime(time.time()))] = msg

    def put(self, *args, **kwargs):
        """ put the job on the queue. """
        self.queue.append((args, kwargs))
        return 

    def stop(self):
        """ stop this worker thread. """
        self.stopped = True
        task = O()
        task.stop = True
        self.put(task)

## dynamically grow threads where needed 

class Dispatcher(O):

    """ the dispatcher can launch additional threads if the current workers are busy. """

    def __init__(self, *args, **kwargs):
        O.__init__(self, *args, **kwargs)
        self.runners = collections.deque() 
        if "max" in kwargs: self.max = kwargs["max"]
        else: self.max = 50

    def stop(self, name=None):
        """ stop all running tasks. """
        for taskrunner in self.runners:
            if name and name not in taskrunner.name: continue
            taskrunner.stop()

    def put(self, *args, **kwargs):
        """ put a function and an event into a job and pass that the a task handler. """
        if not args: raise NoTask()
        target = None
        for taskrunner in self.runners:
            if not len(taskrunner.queue) and not taskrunner.running: target = taskrunner
        if not target: target = self.makenew()
        return target.put(*args, **kwargs)

    def makenew(self, *args, **kwargs):
        """ create a new handler, making sure not more that max nr are running. """
        if len(self.runners) < self.max:
            taskrunner = TaskRunner(*args, **kwargs)
            taskrunner.start()
            self.runners.append(taskrunner)
        else: taskrunner = random.choice(self.runners)
        return taskrunner

    def cleanup(self, dojoin=False):
        """ cleanup finished tasks. """
        todo = []
        for taskrunner in self.runners:
            if taskrunner.stopped or not len(taskrunner.queue): todo.append(taskrunner)
        for taskrunner in todo: taskrunner.stop()
        for taskrunner in todo: self.runners.remove(taskrunner)
