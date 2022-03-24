"""Программа - клиент"""
#   Функции клиента:
#       сформировать presence-сообщение;
#       отправить сообщение серверу;
#       получить ответ сервера;
#       разобрать сообщение сервера;
#       параметры командной строки скрипта client.py <addr> [<port>]:
#           addr — ip-адрес сервера;
#           port — tcp-порт на сервере, по умолчанию 7777.
import argparse
import logging
import log.client_log_config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import unittest
import sys
import time
import json
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, PRESENCE, TIME, \
	USER, ACCOUNT_NAME, RESPONSE, ERROR
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, NonDictInputError
from decorators.decors_def import log
import inspect
from functools import wraps

# Инициализируем клиентский логер
CLIENT_LOGGER = logging.getLogger('client')


# Создает запрос о присутствии клиента
@log
def create_presence(account_name='Guest'):
	message = {
		ACTION: PRESENCE,
		TIME: time.time(),
		USER: {
			ACCOUNT_NAME: account_name,
		}
	}
	CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
	return message


# Разбирает ответ сервера
@log
def process_server_answer(message):
	CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
	if isinstance(message, dict):
		if RESPONSE in message:
			if message[RESPONSE] == 200:
				return '200 : OK'
			return f'400 : {message[ERROR]}'
		raise ReqFieldMissingError(RESPONSE)
	raise NonDictInputError(message)


# Создаем объект parser в котором будут храниться аргументы командной строки
@log
def create_arg_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'address',
		default=DEFAULT_IP_ADDRESS,
		nargs='?',
		help='ip address'
	)
	parser.add_argument(
		'port',
		default=DEFAULT_PORT,
		type=int,
		nargs='?',
		help='port'
	)
	CLIENT_LOGGER.debug(f'Создан объект parser')
	return parser


def main():
	'''
	Загружаем параметры командной строки
	server.py 127.0.0.1 8888
	'''
	# try:
	# 	server_address = sys.argv[1]
	# 	server_port = int(sys.argv[2])
	# 	if server_port < 1024 or server_port > 65535:
	# 		raise ValueError
	# except IndexError:
	# 	server_address = DEFAULT_IP_ADDRESS
	# 	server_port = DEFAULT_PORT
	# except ValueError:
	# 	print('Порт должен быть в диапазоне от 1024 до 65535')
	# 	sys.exit(1)

	parser = create_arg_parser()
	namespace = parser.parse_args(sys.argv[1:])
	server_address = namespace.address
	server_port = namespace.port

	# Проверяем номер порта
	if not 1023 < server_port < 65536:
		CLIENT_LOGGER.critical(
			f'Попытка запуска client с некоректным номером порта: {server_port}.'
			f'Адресс порта должен быть от 1024 до 65535. Программа завершена.'
		)
		sys.exit(1)
	CLIENT_LOGGER.info(
		f'Запущен client с параметрами: '
		f'адрес сервера: {server_address}, порт: {server_port}'
	)

	# Инициализируем сокет
	try:
		serv_sock = socket(AF_INET, SOCK_STREAM)
		serv_sock.connect((server_address, server_port))
		message_to_server = create_presence()
		send_message(serv_sock, message_to_server)
		CLIENT_LOGGER.debug(f'Отправлено сообщение {message_to_server} на server')

		answer = process_server_answer(get_message(serv_sock))
		CLIENT_LOGGER.info(f'Принят ответ от server {answer}')
		print(answer)

	except json.JSONDecodeError:
		CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
		print('Не удалось декодировать сообщение сервера.')

	except ReqFieldMissingError as missing_error:
		CLIENT_LOGGER.error(
			f'В ответе сервера отсутствует необходимое поле '
			f'{missing_error.missing_field}'
		)

	except ConnectionRefusedError:
		CLIENT_LOGGER.critical(
			f'Не удалось подключиться к серверу {server_address}:{server_port}, '
			f'конечный компьютер отверг запрос на подключение.'
		)

	except NonDictInputError:
		CLIENT_LOGGER.error(f'Ответ server не является словарем')


if __name__ == '__main__':
	main()
