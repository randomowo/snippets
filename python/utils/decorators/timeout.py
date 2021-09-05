import functools
import multiprocessing
import logging
import time

from typing import Callable

from .lib import parametrized_dec


@parametrized_dec
def timeout(func: Callable, timeout_=10, name=''):
    """
    Timeout decorator based on multiprocessing lib
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        def queue_wrapper(queue, *args_, **kwargs_):
            queue.put(func(*args_, **kwargs_))

        t = time.time()

        q = multiprocessing.Queue()
        process = multiprocessing.Process(target=queue_wrapper, args=(q, *args), kwargs=kwargs, name=name)
        process.start()
        process.join(timeout=timeout_)
        process.terminate()

        if process.exitcode is not None:
            logging.info(f'Function {func.__name__} excecution took {time.time() - t}s')
            return q.get()
        else:
            logging.warning(f'Function call {func.__name__} timeout exceeded')
            raise Exception('timeout')

    return wrapper
