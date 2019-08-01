"""
Simple timer support for logging elapsed time.

"""
from contextlib import contextmanager
from time import time


@contextmanager
def elapsed_time(target):
    start_time = time()
    try:
        yield start_time
    finally:
        elapsed_ms = (time() - start_time) * 1000
        target["elapsed_time"] = elapsed_ms
