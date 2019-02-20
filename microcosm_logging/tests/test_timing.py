"""
Timing usage tests.

"""
from time import sleep

from hamcrest import assert_that, close_to, is_

from microcosm_logging.timing import elapsed_time


def test_elapsed_time():
    target = dict()
    with elapsed_time(target):
        sleep(0.1)

    assert_that(target["elapsed_time"], is_(close_to(0.1, 0.01)))
