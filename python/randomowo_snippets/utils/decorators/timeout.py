import functools
import multiprocessing
import logging
import time

from typing import Callable

from .lib import parametrized_dec

__all__ = ['timeout']

@parametrized_dec
def timeout(func: Callable, timeout_=10, name=''):
    """
    Timeout decorator based on multiprocessing lib

    use carefully. can take up the entire CPU time untill done.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        def queue_wrapper(queue, *args_, **kwargs_):
            queue.put(func(*args_, **kwargs_))

        start_time = time.time()

        queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=queue_wrapper, args=(queue, *args), kwargs=kwargs, name=name)
        process.start()
        process.join(timeout=timeout_)
        process.terminate()

        if process.exitcode is not None:
            logging.info('Function %s excecution took %fs', func.__name__, time.time() - start_time)
            return queue.get()

        else:
            logging.warning('Function call %s timeout exceeded', func.__name__)
            raise Exception('timeout')

    return wrapper
