"""
Simple timer support for logging elapsed time.

"""
from contextlib import contextmanager
from time import perf_counter


@contextmanager
def elapsed_time(target):
    start_time = perf_counter()
    try:
        yield start_time
    finally:
        elapsed_ms = (perf_counter() - start_time) * 1000
        target["elapsed_time"] = elapsed_ms
