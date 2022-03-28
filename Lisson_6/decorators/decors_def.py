import inspect
import sys
sys.path.append('../')
from common.variables import ENABLE_TRACING
from functools import wraps
import logging, time


def log(func):
    """Функция декоратор"""
    if ENABLE_TRACING:
        @wraps(func)
        def callfunc(*args, **kwargs):
            logger_name = 'server' if 'server.py' in sys.argv[0] else 'client'
            LOGGER = logging.getLogger(logger_name)
            result = func(*args, **kwargs)
            LOGGER.debug(f'Была вызвана функция: <{func.__name__}()>. '
                         f'Вызов из модуля: <{func.__module__}>. '
                         f'Вызов из функции: <{inspect.stack()[1][3]}()>.')
            return result
        return callfunc
    else:
        return func
