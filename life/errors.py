# life/errors.py
#
# life monitoring software

## exceptions

class LifeError(BaseException):
    """ base error class raised in life. """
    pass


class NoFunc(LifeError):
    """ no function is provided. """
    pass

class WrongOType(LifeError):
    """ an otype is being registered on the wrong object. """
    pass

class NotImplemented(LifeError):
    """ this method/function is not implemented. """
    pass

class NoFileName(LifeError):
    """ filename is not set. """
    pass

class NoArgument(LifeError):
    """ no argument was passed to the function/method. """
    pass

class UnknownType(LifeError):
    """ life does not know this type. """
    pass

class NoExec(LifeError):
    """ cannot find an executable (funtion/method) to run. """
    pass

class Denied(LifeError):
    """ No Go. """
    pass

class RatherNot(LifeError):
    """ life does rather not do that. """
    pass

class NoFileName(LifeError):
    """ no filename was set. """
    pass

class NoInput(LifeError):
    """ no input was given. """
    pass

class NoTask(LifeError):
    """ the dispatcher could not determine a task to run. """
    pass

class NoBot(LifeError):
    """ no bot can be found. """
    pass

class NoOrigin(LifeError):
    """ could not determine where event comes from. """
    pass

class RemoteDisconnect(LifeError):
    """ the otherside decided to quit. """
    pass

class SignatureError(LifeError):
    """ stored signatures of data do not match. """
    pass

class RequireError(LifeError):
    """ needed component is not available. """
    pass

class LocateError(LifeError):
    """" cannot find component. """
    pass

class OverloadError(LifeError):
    """ method cannot be overridden. """
    pass

class NotSameType(LifeError):
    """ assigned values need to be of the same type. """
    pass

class NoCommand(LifeError):
    """ command cannot be found. """
    pass

class NoPlugin(LifeError):
    """ plugin cannot be found. """

class NotBooted(LifeError):
    """ L I F E is not initialised yet. Needs boot(). """
    pass

class NoAttribute(LifeError):
    """ requested attribute is not set on object. """
    pass

class NoJSON(LifeError):
    """ object is not JSON. """
    pass

class MissingArg(LifeError):
    """ is missing an argument. """
    pass

class Stop(LifeError):
    """ stop the thing you are doing. """
    pass

class NoBot(LifeError):
    """ no bot was provided in the event being handled. """
    pass

class TryAgain(LifeError):
    """ retry the operation. """
    pass

