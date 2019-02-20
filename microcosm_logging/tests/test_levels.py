"""
Test logging levels.

"""
from logging import INFO, WARNING, getLogger

from hamcrest import assert_that, equal_to, is_

from microcosm_logging.levels import ConditionalLoggingLevel


def test_conditional_level():
    logger = getLogger("foo.bar")

    value = True

    def toggle():
        return value

    level = ConditionalLoggingLevel.setLevel(logger, INFO, WARNING, toggle)

    assert_that(int(level), is_(equal_to(INFO)))
    assert_that(logger.getEffectiveLevel(), is_(equal_to(INFO)))

    value = False

    assert_that(int(level), is_(equal_to(WARNING)))
    assert_that(logger.getEffectiveLevel(), is_(equal_to(WARNING)))
