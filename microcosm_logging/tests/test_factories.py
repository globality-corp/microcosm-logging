from logging import (
    DEBUG,
    INFO,
    WARN,
    getLogger,
)
from os import environ
from unittest import TestCase

from hamcrest import (
    assert_that,
    contains_exactly,
    equal_to,
    is_,
)
from microcosm.api import create_object_graph


class TestFactories(TestCase):

    def test_configure_logging_with_defaults(self):
        """
        Default logging configuration works and enables INFO level logging.

        """
        graph = create_object_graph(name="test", testing=True)

        assert_that(graph.logger, is_(equal_to(getLogger("test"))))
        assert_that(graph.logger.getEffectiveLevel(), is_(equal_to(INFO)))

        graph.logger.info("Info is enabled by default")
        graph.logger.debug("Debug is not enabled by default")

    def test_configure_logging_with_custom_logging_level(self):
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

    def test_configure_logging_with_custom_library_levels(self):
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

    def test_configure_logging_with_invalid_token(self):
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

    def test_extra_and_exc_info(self):
        graph = create_object_graph(name="test", testing=True)

        try:
            raise Exception("error")
        except Exception:
            graph.logger.info(
                "Will include extra info and stack: {foo}",
                exc_info=True,
                extra=dict(foo="bar"),
            )

    def test_configure_logging_with_level_bump(self):
        """
        Logging levels can be bumped.

        """
        def loader(metadata):
            return {
                "logging": {
                    "level": INFO,
                    "levels": {
                        "bump": {
                            "bar": 10,
                        },
                    },
                },
            }

        graph = create_object_graph(name="test", testing=True, loader=loader)
        graph.use("logger")

        with self.assertLogs("foo") as assert_logs:
            getLogger("foo").info("Info message")
            getLogger("foo").warning("Warning message")

        assert_that(assert_logs.output, contains_exactly(
            "INFO:foo:Info message",
            "WARNING:foo:Warning message",
        ))

        with self.assertLogs("bar") as assert_logs:
            getLogger("bar").info("Info message")
            getLogger("bar").warning("Warning message")
            getLogger("bar").critical("Critial message")

        assert_that(assert_logs.output, contains_exactly(
            "WARNING:bar:Info message",
            "ERROR:bar:Warning message",
            "CRITICAL:bar:Critial message",
        ))
