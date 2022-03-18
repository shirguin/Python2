"""Программа-сервер"""
#   Функции сервера:
#       принимает сообщение клиента;
#       формирует ответ клиенту;
#       отправляет ответ клиенту;
#       имеет параметры командной строки:
#           -p <port> — TCP-порт для работы (по умолчанию использует 7777);
#           -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
import json
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import sys
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, RESPONDEFAULT_IP_ADDRESSSE
from common.utils import get_message, send_message


# Обработчик сообщений
def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():

    '''
    Загрузка параметров командной строки
    server.py -p 8888 -a 127.0.0.1
    '''
    # Устанавливаем порт
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После "-p" необходимо указать номер порта')
        sys.exit(1)
    except ValueError:
        print('Выберите порт в диапазоне 1024 - 65535')
        sys.exit(1)

    # Устанавливаем IP адресс
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a')+1]
        else:
            listen_address = ''
    except IndexError:
        print('После параметра "-a" укажите адрес, который будет слушать сервер')
        sys.exit(1)

    # Готовим сокет
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind((listen_address, listen_port))

    # Слушаем порт
    serv_sock.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = serv_sock.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято не корректное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()
