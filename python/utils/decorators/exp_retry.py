import logging
import time
import math
import functools

from typing import Union, Callable, Optional, Tuple, Any, Type

from .lib import parametrized_dec

class ExpRetryExitCallback:
    """Вспомогательный класс для декоратора exp_retry для вызова по завершении"""

    __slots__ = ('callback', 'used_on_class_method', 'args_positions', 'kwargs_name_pairs', )

    def __init__(
            self,
            func: Union[Callable, str],
            used_on_class_method: bool = False,
            args_positions: Optional[Tuple[int, ...]] = None,
            kwargs_name_pairs: Optional[Tuple[Tuple[str, str], ...]] = None
    ):
        """
        Инициализациия колбека для декоратора exp_retry
        :param func: Функция, которая будет вызвана
        :param used_on_class_method: Означает что декораторк exp_retry был использован на методе класса
        :param args_positions: Позиции параметров из функции, на которой был использован декоратор exp_retry, которые
            необходимо педедать в func (как переменные)
        :param kwargs_name_pairs: Пары именованных параметров из функции и имен, которые используются в callback
            функции, на которой был использован декоратор exp_retry, которые необходимо передать в func
            (как именованные переменные)
        """

        if not used_on_class_method and isinstance(func, str):
            raise Exception('Can not use str type of func outside of class')

        self.callback = func
        self.used_on_class_method = used_on_class_method
        self.args_positions = args_positions
        self.kwargs_name_pairs = kwargs_name_pairs

    def __call__(self, *args, **kwargs) -> None:
        """
        Вызов callback функции
        :param args: Параметры переданные из функции, на которой был использован декоратор exp_retry
        :param kwargs: Именованные параметры переданные из функции, на которой был использован декоратор exp_retry
        """
        args_ = args[1:] if self.used_on_class_method else args
        parsed_args = self._parse_args(*args_)
        parsed_kwargs = self._parse_kwargs(**kwargs)
        if self.used_on_class_method and isinstance(self.callback, str):
            getattr(args[0], str(self.callback))(*parsed_args, **parsed_kwargs)

        elif callable(self.callback):
            self.callback(*parsed_args, **parsed_kwargs)

    def _parse_args(self, *args) -> list[Any]:
        if not self.args_positions or len(args) == 0:
            return []

        result = []
        for arg_position in self.args_positions:
            result.append(args[arg_position])

        return result

    def _parse_kwargs(self, **kwargs) -> dict[str, Any]:
        if not self.kwargs_name_pairs or len(kwargs) == 0:
            return {}

        result = {}
        for func_kw_name, callback_kw_name in self.kwargs_name_pairs:
            result[callback_kw_name] = kwargs[func_kw_name]

        return result


@parametrized_dec
def exp_retry(
        func: Callable,
        max_attempts: Optional[int] = None,
        base: int = 2,
        exp_limit: Optional[int] = None,
        skip_exceptions: Optional[Tuple[Type[Exception]]] = None,
        callback_on_exit: Optional[ExpRetryExitCallback] = None,
        raise_after_callback: bool = False
) -> Callable:
    """
    Декоратор для повторного вызова функции при получении ошибки
    :param func: Декорируемая функция
    :param max_attempts: Максимальное количество попыток вызова функции
    :param base: Основание, по которому считается ожидание перед повторным вызовом
    :param exp_limit: Максимальное время ожидания
    :param skip_exceptions: Список исключений, при которых повторный вызов не нужен
    :param callback_on_exit: Callback, который будет вызван по достижении максимального количества попыток или получении
        исключения из списка skip_exceptions
    :param raise_after_callback: Флаг, по которому выбрасывается исключение после выполнения колбека
    :return: Задекорированная функция
    """
    if max_attempts and max_attempts < 1:
        raise ValueError('Argument "max_attempts" must be greater than 0 or None')

    log_suffix: str = 'func name={name} [{{attempt}}/{max_attempts} attempts]'.format(
        name=func.__name__, max_attempts=max_attempts if max_attempts else 'inf'
    )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attempt: int = 1

        while True:
            suffix: str = log_suffix.format(attempt=attempt)
            logging.info('Trying to process function: %s', suffix)

            try:
                func(*args, **kwargs)
            except Exception as exc:
                skip = skip_exceptions and isinstance(exc, skip_exceptions)
                if max_attempts and attempt >= max_attempts or skip:
                    logging.exception(
                        'Unable to process function: %s%s',
                        suffix,
                        ', max attempts reached' if not skip else ''
                    )

                    if callback_on_exit:
                        callback_on_exit(*args, **kwargs)

                        if raise_after_callback:
                            raise exc

                        else:
                            break

                    else:
                        raise exc

                time_s: int = min(base ** (attempt - 1), exp_limit or math.inf)
                logging.exception('Unable to process function, waiting %ds for retry: %s', time_s, suffix)

                time.sleep(time_s)

            else:
                logging.info('Function successfully processed: %s', log_suffix.format(attempt=attempt))
                break

            attempt += 1

    return wrapper
