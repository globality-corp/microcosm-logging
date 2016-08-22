"""Decorator library for common logging functionality."""
from logging import getLogger, LoggerAdapter


def logger(obj):
    """
    logging decorator, assigning an object the `logger` property.
    Can be used on a Python class, e.g:

        @logger
        class MyClass(object):
            ...


    """
    obj.logger = getLogger(obj.__name__)
    return obj


class ContextLogger(LoggerAdapter):
    """
    Allows for inserting additional context into log records based on the current context.
    To play nicely with the pythonjsonlogger used for json logs, a ContextLogger will
    update keys on the existing message object if the message is a dictionary otherwise do nothing.
    The logger does not manipulate string messages because there is no accounting for
    how different handlers want to display what is in self.extra.

    It is possible to write a custom formatter which takes into account for values added to
    self.extra when instantiating the context logger.

    """
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra'].update(self.extra)
        return msg, kwargs


def context_logger(context_func, func, parent=None):
    """
    The results of context_func will be executed and applied to a ContextLogger
    instance for the execution of func. The resulting ContextLogger instance will be
    available on parent.logger for the duration of func.

    :param context_func: callable which provides dictionary-like context information
    :param func: the function to wrap
    :param parent: object to attach the context logger to, if None, defaults to func.__self__
    """
    if parent is None:
        parent = func.__self__

    def wrapped(*args, **kwargs):
        parent.logger = ContextLogger(
            getattr(parent, 'logger', getLogger(parent.__class__.__name__)),
            context_func(*args, **kwargs) or dict(),
        )
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            parent.logger = parent.logger.logger
    return wrapped
