"""
Test logging levels.

"""
from logging import getLogger, INFO, WARNING
from hamcrest import assert_that, equal_to, is_

from microcosm_logging.levels import ConditionalLoggingLevel


def test_conditional_level():
    logger = getLogger("foo.bar")

    value = True

    def toggle():
        return value

    ConditionalLoggingLevel.setLevel(logger, INFO, WARNING, toggle)

    assert_that(logger.getEffectiveLevel(), is_(equal_to(INFO)))

    value = False

    assert_that(logger.getEffectiveLevel(), is_(equal_to(WARNING)))
