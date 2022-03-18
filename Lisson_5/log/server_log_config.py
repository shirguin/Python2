"""Настройка логгера для server"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import sys
sys.path.append('../')
from common.variables import LEVEL_LOGGING

# Задаем формат логов
SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s %(message)s')

# Подготовка имени лог файла

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# Создаем обработчики логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

# FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')

# Ротация по длине файла равной 1500 байт
# FILE_HANDLER = RotatingFileHandler(PATH, encoding='utf-8', maxBytes=1500, backupCount=5)

# ротация с интервалом 1 минута
# FILE_HANDLER = TimedRotatingFileHandler(PATH, encoding='utf-8', when='M', interval=1, backupCount=5)

# ротация логфайла раз в сутки в полночь
FILE_HANDLER = TimedRotatingFileHandler(PATH, encoding='utf-8', when='H', interval=24, backupCount=5, atTime=None)
FILE_HANDLER.setFormatter(SERVER_FORMATTER)

# Создаем регистратор
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LEVEL_LOGGING)


# Проверка работы логирования
def main():
    LOGGER.info('Просто информация')
    LOGGER.debug('Отладочная информация')
    LOGGER.error('Сообщение об ощибке')
    LOGGER.critical('Критическая ошибка')


if __name__ == '__main__':
    main()
