"""Программа-сервер"""
#   Функции сервера:
#       принимает сообщение клиента;
#       формирует ответ клиенту;
#       отправляет ответ клиенту;
#       имеет параметры командной строки:
#           -p <port> — TCP-порт для работы (по умолчанию использует 7777);
#           -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
import argparse
import json
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, RESPONDEFAULT_IP_ADDRESSSE
from common.utils import get_message, send_message
import logging
import log.server_log_config
from errors import IncorrectDataReceivedError, NonDictInputError
from decorators.decors_def import log
import inspect
from functools import wraps
import time

# Инициализируем серверный логер
SERVER_LOGGER = logging.getLogger('server')


# Обработчик сообщений
@log
def process_client_message(message):
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
    if isinstance(message, dict):
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
    raise NonDictInputError(message)


# Создаем объект parser в котором будут храниться аргументы командной строки
@log
def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        default=DEFAULT_PORT,
        type=int,
        nargs='?',
        help='port'
    )
    parser.add_argument(
        '-a',
        default='',
        nargs='?',
        help='ip address'
    )
    SERVER_LOGGER.debug(f'Создан объект parser')
    return parser


def main():

    '''
    Загрузка параметров командной строки
    server.py -p 8888 -a 127.0.0.1
    '''

    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # Проверка адреса порта
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с некоректным адрессом порта '
            f'{listen_port}. Допустимы адреса с 1024 по 65535.'
        )
        sys.exit(1)
    SERVER_LOGGER.info(
        f'Запущен server !'
        f'Порт для подключений: {listen_port},'
        f'Адрес с которого принимаются подключения: {listen_address}.'
        f'Если адрес не указан, принимаются соединения с любых адресов.'
    )

    # Готовим сокет
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.bind((listen_address, listen_port))

    # Слушаем порт
    serv_sock.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = serv_sock.accept()
        SERVER_LOGGER.info(f'Установлено соединение с client {client_address}')
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение от client {message_from_client}')
            print(message_from_client)

            response = process_client_message(message_from_client)
            SERVER_LOGGER.debug(f'Сформирован ответ client {response}')

            send_message(client, response)
            SERVER_LOGGER.info(f'Отправлен ответ client {response}')

            client.close()
            SERVER_LOGGER.info(f'Соединение с клиентом {client_address} закрыто.')

        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Не удалось декодировать JSON строку, полученную от client {client_address}')
            print('Принято не корректное сообщение от клиента')

            client.close()
            SERVER_LOGGER.info(f'Соединение с клиентом {client_address} закрыто.')

        except IncorrectDataReceivedError:
            SERVER_LOGGER.error(f'От клиента {client_address} приняты некорректные данные. ')
            client.close()
            SERVER_LOGGER.info(f'Соединение с клиентом {client_address} закрыто.')

        except NonDictInputError:
            SERVER_LOGGER.error(f'Ответ client не является словарем')


if __name__ == '__main__':
    main()
