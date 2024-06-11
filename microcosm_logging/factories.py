"""
Factory that configures logging.

"""
from logging import (
    CRITICAL,
    getLogger,
    getLogRecordFactory,
    setLogRecordFactory,
)
from logging.config import dictConfig
from os import environ

from microcosm.api import defaults, typed


@defaults(
    default_format="{asctime} - {name} - [{levelname}] - {message}",
    json_required_keys="%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(levelno) - %(message)s",

    https_handler=dict(
        class_="loggly.handlers.HTTPSHandler",
    ),

    json_formatter=dict(
        formatter="pythonjsonlogger.jsonlogger.JsonFormatter",
    ),

    # default log level is INFO
    level="INFO",

    # tune down some common libraries
    levels=dict(
        default=dict(
            debug=[],
            info=[
                "boto",
                "newrelic",
            ],
            warn=[
                "aws_encryption_sdk",
                "botocore.vendored.requests",
                "bravado_core",
                "requests",
                "swagger_spec_validator",
            ],
            error=[
                "bravado.requests_client",
                "FuturesSession",
            ],
        ),
        override=dict(
            debug=[],
            info=[],
            warn=[],
            error=[],
        ),
        bump=dict(),
    ),

    # loggly
    loggly=dict(
        base_url="https://logs-01.loggly.com",
    ),

    # logstash
    logstash=dict(
        enabled=typed(bool, default_value=False),
        host="localhost",
        port=5959,
    ),

    # configure stream handler
    stream_handler=dict(
        class_="logging.StreamHandler",
        formatter="ExtraFormatter",
        stream="ext://sys.stdout",
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


def enable_loggly(graph):
    """
    Enable loggly if it is configured and not debug/testing.

    """
    if graph.metadata.debug or graph.metadata.testing:
        return False

    try:
        if not graph.config.logging.loggly.token:
            return False

        if not graph.config.logging.loggly.environment:
            return False
    except AttributeError:
        return False

    return True


def make_dict_config(graph):
    """
    Build a dictionary configuration from conventions and configuration.

    """
    formatters = {}
    handlers = {}
    loggers = {}

    # create formatters
    formatters["ExtraFormatter"] = make_extra_console_formatter(graph)
    formatters["JSONFormatter"] = make_json_formatter(graph)

    # create the console handler with the configured formatter
    handlers["console"] = make_stream_handler(graph, formatter=graph.config.logging.stream_handler.formatter)

    # maybe create the loggly handler
    if enable_loggly(graph):
        handlers["LogglyHTTPSHandler"] = make_loggly_handler(graph, formatter="JSONFormatter")

    # create the logstash handler only if explicitly configured
    if graph.config.logging.logstash.enabled:
        handlers["LogstashHandler"] = make_logstash_handler(graph)

    # configure the root logger to output to all handlers
    loggers[""] = {
        "handlers": handlers.keys(),
        "level": graph.config.logging.level,
    }

    # set log levels for libraries
    loggers.update(make_library_levels(graph))
    bump_library_levels(graph)

    return dict(
        version=1,
        disable_existing_loggers=False,
        formatters=formatters,
        handlers=handlers,
        loggers=loggers,
    )


def make_json_formatter(graph):
    """
    Create the default json formatter.

    """

    return {
        "()": graph.config.logging.json_formatter.formatter,
        "fmt": graph.config.logging.json_required_keys,
    }


def make_extra_console_formatter(graph):
    """
    Create the default console formatter.

    """

    return {
        "()": "microcosm_logging.formatters.ExtraConsoleFormatter",
        "format_string": graph.config.logging.default_format,
    }


def make_stream_handler(graph, formatter):
    """
    Create the stream handler. Used for console/debug output.

    """
    return {
        "class": graph.config.logging.stream_handler.class_,
        "formatter": formatter,
        "level": graph.config.logging.level,
        "stream": graph.config.logging.stream_handler.stream,
    }


def make_loggly_handler(graph, formatter):
    """
    Create the loggly handler.

    Used for searchable aggregation.

    """
    base_url = graph.config.logging.loggly.base_url
    metric_service_name = environ.get("METRICS_NAME", graph.metadata.name)
    loggly_url = "{}/inputs/{}/tag/{}".format(
        base_url,
        graph.config.logging.loggly.token,
        ",".join({
            graph.metadata.name,
            graph.config.logging.loggly.environment,
            metric_service_name,
        }),
    )
    return {
        "class": graph.config.logging.https_handler.class_,
        "formatter": formatter,
        "level": graph.config.logging.level,
        "url": loggly_url,
    }


def make_logstash_handler(graph):
    """
    Create the logstash handler

    Relies on a temporary directory for the locally-cached database path
    that is then streamed to a local logstash daemon. This is created in
    the OS temp storage and will be garbage collected at an appropriate time.

    """
    return {
        "class": "logstash_async.handler.SynchronousLogstashHandler",
        "host": graph.config.logging.logstash.host,
        "port": graph.config.logging.logstash.port,
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


def bump_level_factory(mapping: dict[str, int]):
    factory = getLogRecordFactory()

    def apply(name, level, *args, **kwargs):
        return factory(
            name,
            min(level + mapping.get(name, 0), CRITICAL),
            *args,
            **kwargs,
        )

    return apply


def bump_library_levels(graph):
    if not graph.config.logging.levels.bump:
        return

    setLogRecordFactory(
        bump_level_factory(graph.config.logging.levels.bump),
    )
