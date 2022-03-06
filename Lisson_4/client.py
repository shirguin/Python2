"""Программа - клиент"""
#   Функции клиента:
#       сформировать presence-сообщение;
#       отправить сообщение серверу;
#       получить ответ сервера;
#       разобрать сообщение сервера;
#       параметры командной строки скрипта client.py <addr> [<port>]:
#           addr — ip-адрес сервера;
#           port — tcp-порт на сервере, по умолчанию 7777.

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import unittest
import sys
import time
import json
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, PRESENCE, TIME, \
	USER, ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import get_message, send_message


# Создает запрос о присутствии клиента
def create_presence(account_name='Guest'):
	message = {
		ACTION: PRESENCE,
		TIME: time.time(),
		USER: {
			ACCOUNT_NAME: account_name,
		}
	}
	return message


# Разбирает ответ сервера
def process_server_answer(message):
	if RESPONSE in message:
		if message[RESPONSE] == 200:
			return '200 : OK'
		return f'400 : {message[ERROR]}'
	raise ValueError


def main():
	'''
	Загружаем параметры командной строки
	server.py 127.0.0.1 8888
	'''
	try:
		server_address = sys.argv[1]
		server_port = int(sys.argv[2])
		if server_port < 1024 or server_port > 65535:
			raise ValueError
	except IndexError:
		server_address = DEFAULT_IP_ADDRESS
		server_port = DEFAULT_PORT
	except ValueError:
		print('Порт должен быть в диапазоне от 1024 до 65535')
		sys.exit(1)

	# Инициализируем сокет
	serv_sock = socket(AF_INET, SOCK_STREAM)
	serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serv_sock.connect((server_address, server_port))
	message_to_server = create_presence()
	send_message(serv_sock, message_to_server)
	try:
		answer = process_server_answer(get_message(serv_sock))
		print(answer)
	except (ValueError, json.JSONDecodeError):
		print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
	main()
