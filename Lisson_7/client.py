"""Программа - клиент"""

import argparse
import logging
import log.client_log_config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import unittest
import sys
import time
import json
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, PRESENCE, TIME, \
	USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, NonDictInputError, ServerError
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


@log
def create_message(sock, account_name='Guest'):
	"""Функция запрашивает текст сообщения и возвращает его.
	Так же завершает работу при вводе подобной комманды"""
	message = input('Введите сообщение для отправки или \"exit\" для завершения работы: ')
	if message == 'exit':
		sock.close()
		CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
		print('Спасибо за использование сервиса!')
		sys.exit(0)
	message_dict = {
		ACTION: MESSAGE,
		TIME: time.time(),
		ACCOUNT_NAME: account_name,
		MESSAGE_TEXT: message
	}
	CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
	return message_dict


@log
def message_from_server(message):
	"""Функция - обработчик сообщений других пользователей, поступающих с сервера"""
	if ACTION in message and message[ACTION] == MESSAGE and \
			SENDER in message and MESSAGE_TEXT in message:
		print(f'Получено сообщение от пользователя '
				f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
		CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
					f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
	else:
		CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


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


# Создаём парсер аргументов коммандной строки
# и читаем параметры, возвращаем 3 параметра
@log
def arg_parser():
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
	parser.add_argument(
		'-m',
		'--mode',
		default='listen',
		nargs='?',
		help='mode'
	)
	namespace = parser.parse_args(sys.argv[1:])
	server_address = namespace.address
	server_port = namespace.port
	client_mode = namespace.mode

	# Проверяем номер порта
	if not 1023 < server_port < 65536:
		CLIENT_LOGGER.critical(
			f'Попытка запуска client с некоректным номером порта: {server_port}.'
			f'Адресс порта должен быть от 1024 до 65535. Программа завершена.'
		)
		sys.exit(1)

	# Проверяем допустим ли выбранный режим работы клиента
	if client_mode not in ('listen', 'send'):
		CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
							   f'допустимые режимы: listen, send')
		sys.exit(1)

	return server_address, server_port, client_mode


def main():
	'''
	Загружаем параметры командной строки
	server.py 127.0.0.1 8888 -m send/listen
	'''
	server_address, server_port, client_mode = arg_parser()

	CLIENT_LOGGER.info(
		f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
		f'порт: {server_port}, режим работы: {client_mode}'
	)

	# Инициализируем сокет
	try:
		serv_sock = socket(AF_INET, SOCK_STREAM)
		serv_sock.connect((server_address, server_port))
		send_message(serv_sock, create_presence())
		answer = process_server_answer(get_message(serv_sock))
		CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
		print(f'Установлено соединение с сервером.')
	except json.JSONDecodeError:
		CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
		print('Не удалось декодировать сообщение сервера.')
		sys.exit(1)
	except ServerError as error:
		CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
		sys.exit(1)
	except ReqFieldMissingError as missing_error:
		CLIENT_LOGGER.error(
			f'В ответе сервера отсутствует необходимое поле '
			f'{missing_error.missing_field}'
		)
		sys.exit(1)
	except ConnectionRefusedError:
		CLIENT_LOGGER.critical(
			f'Не удалось подключиться к серверу {server_address}:{server_port}, '
			f'конечный компьютер отверг запрос на подключение.'
		)
		sys.exit(1)
	except NonDictInputError:
		CLIENT_LOGGER.error(f'Ответ сервера не является словарем')
		sys.exit(1)
	else:
		# Соединение с сервером установлено корректно
		if client_mode == 'send':
			print('Режим работы: отправка сообщений')
		else:
			print('Режим работы: прием сообщений')

		# Основной цикл программы
	while True:
		# Режим: отправка сообщений
		if client_mode == 'send':
			try:
				send_message(serv_sock, create_message(serv_sock))
			except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
				CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
				sys.exit(1)

		# Режим: прием сообщений
		if client_mode == 'listen':
			try:
				message_from_server(get_message(serv_sock))
			except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
				CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
				sys.exit(1)


if __name__ == '__main__':
	main()
