from logging import DEBUG, getLogger

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm_logging.decorators import logger


@logger
class TestClass(object):

    pass


def test_using_class_logger_works():
    instance = TestClass()

    assert_that(instance.logger, is_(equal_to(getLogger(instance.__class__.__name__))))
    assert_that(instance.logger.getEffectiveLevel(), is_(equal_to(DEBUG)))
