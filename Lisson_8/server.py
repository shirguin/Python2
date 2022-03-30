"""Программа-сервер"""

import argparse
import json
import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, RESPONDEFAULT_IP_ADDRESSSE, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, RESPONSE_200, RESPONSE_400, EXIT
from common.utils import get_message, send_message
import logging
import log.server_log_config
from decorators.decors_def import log


# Инициализируем серверный логер
SERVER_LOGGER = logging.getLogger('server')


# Обработчик сообщений
@log
def process_client_message(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')

    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return

    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return

    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return

    # Иначе отдаём Bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


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
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind((listen_address, listen_port))
    serv_sock.settimeout(0.5)

    clients = []
    messages = []
    names = dict()  # {client_name: client_socket}

    # Слушаем порт
    serv_sock.listen(MAX_CONNECTIONS)

    # Основной цикл Сервера
    while True:
        try:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            client, client_address = serv_sock.accept()
        except OSError as err:
            pass
        else:
            SERVER_LOGGER.debug(f'Установлено соединение с клиентом: {client_address}')
            clients.append(client)
        finally:
            wait = 0
            received_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    received_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], wait)
            except OSError:
                pass

            # Принимаем сообщения и сохраняем в словаре, если ошибка, удаляем клиента
            if received_data_lst:
                for client_with_message in received_data_lst:
                    try:
                        process_client_message(get_message(client_with_message), messages, client_with_message, clients, names)
                    except:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for el in messages:
                try:
                    process_message(el, names, send_data_lst)
                except Exception:
                    SERVER_LOGGER.info(f'Связь с клиентом: {el[DESTINATION]} была потеряна')
                    clients.remove(names[el[DESTINATION]])
                    del names[el[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    main()
