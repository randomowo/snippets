from typing import Callable
import functools

__all__ = [
    'parametrized_dec'
]

def parametrized_dec(dec) -> Callable:
    @functools.wraps(dec)
    def layer(*args, **kwargs) -> Callable:

        @functools.wraps(dec)
        def repl(f) -> Callable:
            return dec(f, *args, **kwargs)

        return repl
    return layer


