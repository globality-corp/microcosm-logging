"""
Logging levels

"""
from functools import total_ordering


@total_ordering
class ConditionalLoggingLevel:
    """
    A logging level that is conditional on a function.

    Works by masquerading as an int.

    """
    def __init__(self, true_levelno, false_levelno, func):
        self._true_levelno = true_levelno
        self._false_levelno = false_levelno
        self._func = func

    @property
    def levelno(self):
        if self._func():
            return self._true_levelno
        else:
            return self._false_levelno

    def __int__(self):
        return self.levelno

    def __str__(self):
        return str(self.levelno)

    def __repr__(self):
        return str(self.levelno)

    def __eq__(self, other):
        if hasattr(other, "levelno"):
            return self.levelno == other.levelno
        else:
            return self.levelno == other

    def __lt__(self, other):
        if hasattr(other, "levelno"):
            return self.levelno < other.levelno
        else:
            return self.levelno < other

    @classmethod
    def setLevel(cls, logger, *args, **kwargs):
        """
        Set a conditional log level.

        """
        # NB: set `logger.level` because loggers validate the type of the input to `logger.setLevel()`
        logger.level = level = cls(*args, **kwargs)
        return level
