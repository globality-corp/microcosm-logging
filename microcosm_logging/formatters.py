from logging import Formatter

from pythonjsonlogger.jsonlogger import merge_record_extra


class ExtraConsoleFormatter(Formatter):
    """
    An extension of the builtin logging.Formatter which allows for logging
    messages in the format:

        `self.logger.info("Message {foo}.", extra=dict(foo='bar'))`

    To produce messages of the format:

        `Message bar.`

    Besides having the ability to substitue values from extra into the message
    record, this formatter is consistent with the builtin logging.Formatter.

    """

    def __init__(self, format_string):
        self.format_string = format_string

    def format(self, record):
        message = record.getMessage()

        extra = merge_record_extra(record, dict())
        if not isinstance(record.msg, dict):
            message = message.format(**extra)

        if self.format_string.find("%(asctime)") >= 0:
            record.asctime = self.formatTime(record, self.datefmt)

        log_string = self.format_string.format(
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
