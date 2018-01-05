from logging import getLogger

from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)

from mock import Mock

from microcosm_logging.decorators import logger, context_logger


@logger
class TestClass:

    pass


@logger
class TestContextClass:

    def function(self):
        self.logger.info("success!")


def test_using_class_logger_works():
    instance = TestClass()

    assert_that(instance.logger, is_(equal_to(getLogger(instance.__class__.__name__))))


def test_using_context_logger_works():
    instance = TestContextClass()
    context_func = Mock(return_value={'some': 'context'})
    wrapped = context_logger(context_func, instance.function, instance)

    wrapped()
    context_func.assert_called_once()


def test_using_context_logger_no_parent():
    instance = TestContextClass()
    context_func = Mock(return_value={'some': 'context'})
    wrapped = context_logger(context_func, instance.function)

    wrapped()
    context_func.assert_called_once()


def test_using_context_logger_no_parent_no_class_fails():
    def function():
        pass

    context_func = Mock(return_value={'some': 'context'})
    assert_that(
        calling(context_logger).with_args(context_func, function),
        raises(AttributeError),
    )
