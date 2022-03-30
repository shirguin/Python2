"""Программа-сервер"""

import argparse
import json
import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, RESPONDEFAULT_IP_ADDRESSSE, MESSAGE, MESSAGE_TEXT, SENDER
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
def process_client_message(message, messages_list, client):
    """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
        проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
        :param message:
        :param messages_list:
        :param client:
        :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')
    if isinstance(message, dict):
        # Если это сообщение о присутствии, принимаем и отвечаем, если успех
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            send_message(client, {RESPONSE: 200})
            return

        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                TIME in message and MESSAGE_TEXT in message:
            messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
            return
        # Иначе отдаём Bad request
        else:
            send_message(client, {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            })

    raise NonDictInputError(message)


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
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

    return listen_address, listen_port


def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port = arg_parser()

    SERVER_LOGGER.info(
        f'Запущен server !'
        f'Порт для подключений: {listen_port},'
        f'Адрес с которого принимаются подключения: {listen_address}.'
        f'Если адрес не указан, принимаются соединения с любых адресов.'
    )

    # Готовим сокет
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.bind((listen_address, listen_port))
    serv_sock.settimeout(0.5)

    clients = []
    messages = []

    # Слушаем порт
    serv_sock.listen(MAX_CONNECTIONS)

    # Основной цикл Сервера
    while True:
        try:
            client, client_address = serv_sock.accept()
        except OSError as err:
            print(err.errno) # Печатает номер ошибки. Будет None так, как это просто тайм-аут
            pass
        else:
            SERVER_LOGGER.debug(f'Установлено соединение с клиентом: {client_address}')
            clients.append(client)
        finally:
            wait = 0
            received_data_lst = []
            send_data_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    received_data_lst, send_data_lst, _ = select.select(clients, clients, [], wait)
            except OSError:
                pass # Ничего не делать если какой-то клиент отключился

            # Принимаем сообщения и сохраняем в словаре, если ошибка, удаляем клиента
            if received_data_lst:
                for client_with_message in received_data_lst:
                    try:
                        process_client_message(get_message(client_with_message), messages, client_with_message)
                    except:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            if messages and send_data_lst:
                message = {
                    ACTION: MESSAGE,
                    SENDER: messages[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: messages[0][1]
                }
                del messages[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, message)
                    except:
                        SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        waiting_client.close()
                        clients.remove(waiting_client)


if __name__ == '__main__':
    main()
