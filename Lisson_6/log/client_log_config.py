"""Настройка логгера для client"""

import logging
import os
import sys
sys.path.append('../')
from common.variables import LEVEL_LOGGING

# Задаем формат логов
CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)-8s %(filename)-18s %(message)s')

# Подготовка имени log-файла
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

# Создаем обработчики логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
FILE_HANDLER.setFormatter(CLIENT_FORMATTER)

# Создаем регистратор
LOGGER = logging.getLogger('client')
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
