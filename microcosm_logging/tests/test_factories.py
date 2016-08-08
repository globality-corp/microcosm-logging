from logging import getLogger, DEBUG, INFO, WARN
from os import environ

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)
from microcosm.api import create_object_graph


def test_configure_logging_with_defaults():
    """
    Default logging configuration works and enables INFO level logging.

    """
    graph = create_object_graph(name="test", testing=True)

    assert_that(graph.logger, is_(equal_to(getLogger("test"))))
    assert_that(graph.logger.getEffectiveLevel(), is_(equal_to(INFO)))

    graph.logger.info("Info is enabled by default")
    graph.logger.debug("Debug is not enabled by default")


def test_configure_logging_with_custom_logging_level():
    """
    The system-wide logging level can be overridden.

    """
    def loader(metadata):
        return dict(
            logging=dict(
                level="DEBUG",
            )
        )

    graph = create_object_graph(name="test", testing=True, loader=loader)

    assert_that(graph.logger.getEffectiveLevel(), is_(equal_to(DEBUG)))

    graph.logger.info("Info is enabled by default")
    graph.logger.debug("Debug is enabled by configuration")


def test_configure_logging_with_custom_library_levels():
    """
    Logging levels can be configured.

    """
    def loader(metadata):
        return dict(
            logging=dict(
                level=INFO,
                levels=dict(
                    default=dict(
                        debug=["foo", "bar"],
                    ),
                    override=dict(
                        warn=["foo"],
                    )
                )
            )
        )

    graph = create_object_graph(name="test", testing=True, loader=loader)
    graph.use("logger")

    assert_that(getLogger("foo").getEffectiveLevel(), is_(equal_to(WARN)))
    assert_that(getLogger("bar").getEffectiveLevel(), is_(equal_to(DEBUG)))

    getLogger("bar").info("Bar should be visible at info")
    getLogger("foo").info("Foo should not be visible at info")
    getLogger("foo").warn("Foo should be visible at warn")


def test_configure_logging_with_invalid_token():
    """
    Enabling loggly.

    """
    def loader(metadata):
        return dict(
            logging=dict(
                loggly=dict(
                    token=environ.get("LOGGLY_TOKEN", "TOKEN"),
                    environment="unittest",
                )
            )
        )

    graph = create_object_graph(name="test", loader=loader)
    graph.use("logger")

    graph.logger.info("Info will appear in loggly if LOGGLY_TOKEN is set correctly.")
