from logging import getLogger

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
