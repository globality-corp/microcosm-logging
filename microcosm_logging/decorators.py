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
    update keys on the existing message object if the message is a dictionary otherwise,
    it will prepend context information before the log message in brackets.

    """
    def process(self, msg, kwargs):
        if isinstance(msg, dict):
            msg.update(self.extra)
        else:
            headers_string = [
                '{header_name}: {header_value}'.format(
                    header_name=header_name,
                    header_value=header_value
                ) for header_name, header_value in self.extra.iteritems()
            ]
            msg = '{} {}'.format(
                "[{}]".format(" ,".join(headers_string)),
                msg
            )
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
            context_func(*args, **kwargs),
        )
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            parent.logger = parent.logger.logger
    return wrapped
