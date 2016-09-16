from logging import Formatter

from pythonjsonlogger.jsonlogger import merge_record_extra


class ExtraConsoleFormatter(Formatter):
    """
    An extension of the builtin logging.Formatter which allows for logging
    messages in the format:

        `self.logger.info("Message {foo}.", extra=dict(foo='bar'))`

    To produce messages of the format:

        `Message bar.`

    Besides having the ability to substitute values from `extra` into the message
    record, this formatter is consistent with the builtin logging.Formatter.

    """

    def __init__(self, format_string):
        self.format_string = format_string

    def format(self, record):
        message = record.getMessage()

        extra = merge_record_extra(record, dict())
        if not isinstance(record.msg, dict) and extra:
            message = self.format_safely(message, **extra)

        if self.format_string.find("%(asctime)") >= 0:
            record.asctime = self.formatTime(record, self.datefmt)

        log_string = self.format_safely(
            self.format_string,
            asctime=self.formatTime(record),
            name=record.name,
            levelname=record.levelname,
            message=message
        )

        if record.exc_info:
            if log_string[-1] != "\n":
                log_string = log_string + "\n"
            log_string = log_string + self.formatException(record.exc_info)

        return log_string

    def format_safely(self, s, **kwargs):
        # support old-style formatting
        try:
            result = s % kwargs
        except (KeyError, SyntaxError, TypeError):
            pass
        else:
            if result != s:
                return result

        # support new-style formatting
        try:
            return s.format(**kwargs)
        except KeyError:
            pass

        # some messages will use '{' and '}' without meaning to use format strings
        return s
