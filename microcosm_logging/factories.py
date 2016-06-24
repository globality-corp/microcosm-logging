"""
Factory that configures logging.

"""
from logging import getLogger
from logging.config import dictConfig

from microcosm.api import defaults


@defaults(
    # default log level is INFO
    level="INFO",

    # tune down some common libraries
    levels=dict(
        default=dict(
            debug=[],
            info=["boto", "newrelic"],
            warn=["requests", "botocore.vendored.requests"],
            error=[],
        ),
        override=dict(
            debug=[],
            info=[],
            warn=[],
            error=[],
        ),
    ),

    # loggly is enabled (unless debug/testing are set)
    loggly=dict(
        enabled=True,
    ),
)
def configure_logging(graph):
    """
    Configure logging using a constructed dictionary config.

     - Tunes logging levels.
     - Sets up console and, if not in debug, loggly output.

    :returns: a logger instance of the configured name

    """
    dict_config = make_dict_config(graph)
    dictConfig(dict_config)
    return True


def configure_logger(graph):
    """
    Configure application logger.

    """
    graph.use("logging")
    return getLogger(graph.metadata.name)


def make_dict_config(graph):
    """
    Build a dictionary configuration from conventions and configuration.

    """
    formatters = {}
    handlers = {}
    loggers = {}

    # create the console handler
    formatters["default"] = make_default_formatter(graph)
    handlers["console"] = make_stream_handler(graph, formatter="default")

    # maybe create the loggly handler
    if not any((graph.metadata.debug, graph.metadata.testing)) and graph.config.logging.loggly.enabled:
        formatters["JSONFormatter"] = make_json_formatter(graph)
        handlers["LogglyHTTPSHandler"] = make_loggly_handler(graph, formatter="JSONFormatter")

    # configure the root logger to output to all handlers
    loggers[""] = {
        "handlers": handlers.keys(),
        "level": graph.config.logging.level,
    }

    # set log levels for libraries
    loggers.update(make_library_levels(graph))

    return dict(
        version=1,
        disable_existing_loggers=False,
        formatters=formatters,
        handlers=handlers,
        loggers=loggers,
    )


def make_default_formatter(graph):
    """
    Create the default log formatter.

    Used for console/debug logging.

    """
    return {
        "format": "%(asctime)s - %(name)-12s - [%(levelname)s] - %(message)s"
    }


def make_json_formatter(graph):
    """
    Create the JSON log formatter.

    Used for searchable aggregation.

    """
    fields = [
        'asctime',
        'levelname',
        'name',
        'filename',
        'funcName',
        'lineno',
        'message',
    ]

    formatter = "pythonjsonlogger.jsonlogger.JsonFormatter"
    format = " ".join("%({})".format(field) for field in fields)

    return {
        '()': formatter,
        "format": format,
    }


def make_stream_handler(graph, formatter):
    """
    Create the stream handler. Used for console/debug output.

    """
    return {
        "class": "logging.StreamHandler",
        "formatter": formatter,
        "level": graph.config.logging.level,
        "stream": "ext://sys.stdout",
    }


def make_loggly_handler(graph, formatter):
    """
    Create the loggly handler.

    Used for searchable aggregation.

    """
    base_url = graph.config.logging.loggly.get("base_url", "https://logs-01.loggly.com")
    loggly_url = "{}/inputs/{}/tag/{}".format(
        base_url,
        graph.config.logging.loggly.token,
        ",".join([
            "python",
            graph.metadata.name,
            graph.config.logging.loggly.environment,
        ]),
    )
    return {
        "class": "loggly.handlers.HTTPSHandler",
        "formatter": formatter,
        "level": graph.config.logging.level,
        "url": loggly_url,
    }


def make_library_levels(graph):
    """
    Create third party library logging level configurations.

    Tunes down overly verbose logs in commonly used libraries.

    """
    # inject the default components; these can, but probably shouldn't, be overridden
    levels = {}
    for level in ["DEBUG", "INFO", "WARN", "ERROR"]:
        levels.update({
            component: {
                "level": level,
            } for component in graph.config.logging.levels.default[level.lower()]
        })
    # override components; these can be set per application
    for level in ["DEBUG", "INFO", "WARN", "ERROR"]:
        levels.update({
            component: {
                "level": level,
            } for component in graph.config.logging.levels.override[level.lower()]
        })
    return levels
