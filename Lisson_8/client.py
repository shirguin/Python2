"""Программа - клиент"""

import argparse
import logging
import threading

import log.client_log_config
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import unittest
import sys
import time
import json
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, PRESENCE, TIME, \
	USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, NonDictInputError, ServerError
from decorators.decors_def import log
import inspect
from functools import wraps

# Инициализируем клиентский логер
CLIENT_LOGGER = logging.getLogger('client')


# Создает запрос о присутствии клиента
@log
def create_presence(account_name):
	"""Функция генерирует запрос о присутствии клиента"""
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
	to_user = input('Введите получателя сообщения: ')
	message = input('Введите сообщение для отправки: ')
	message_dict = {
		ACTION: MESSAGE,
		SENDER: account_name,
		DESTINATION: to_user,
		TIME: time.time(),
		MESSAGE_TEXT: message
	}
	CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
	try:
		send_message(sock, message_dict)
		CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
	except Exception as e:
		print(e)
		CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
		sys.exit(1)


@log
def create_exit_message(account_name):
	"""Функция создаёт словарь с сообщением о выходе"""
	return {
		ACTION: EXIT,
		TIME: time.time(),
		ACCOUNT_NAME: account_name
	}


@log
def message_from_server(sock, my_username):
	"""Функция - обработчик сообщений других пользователей, поступающих с сервера"""
	while True:
		try:
			message = get_message(sock)
			if ACTION in message and message[ACTION] == MESSAGE and \
					SENDER in message and DESTINATION in message \
					and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
				print(f'\nПолучено сообщение от пользователя '
						f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
				CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
							f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
			else:
				CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
		except (OSError, ConnectionError, ConnectionAbortedError,
				ConnectionResetError, json.JSONDecodeError):
			CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
			break

# Разбирает ответ сервера
@log
def process_server_answer(message):
	CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
	if RESPONSE in message:
		if message[RESPONSE] == 200:
			return '200 : OK'
		elif message[RESPONSE] == 400:
			raise ServerError(f'400 : {message[ERROR]}')
	raise ReqFieldMissingError(RESPONSE)


def print_help():
	"""Функция выводящяя справку по использованию"""
	print('Поддерживаемые команды:')
	print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
	print('help - вывести подсказки по командам')
	print('exit - выход из программы')


@log
def user_interactive(sock, username):
	"""Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
	print_help()
	while True:
		command = input('Введите команду: ')
		if command == 'message':
			create_message(sock, username)
		elif command == 'help':
			print_help()
		elif command == 'exit':
			send_message(sock, create_exit_message(username))
			print('Завершение соединения.')
			CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
			# Задержка неоходима, чтобы успело уйти сообщение о выходе
			time.sleep(0.5)
			break
		else:
			print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


@log
def arg_parser():
	"""Парсер аргументов коммандной строки"""
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
		'-n',
		'--name',
		default=None,
		nargs='?',
		help='name'
	)
	namespace = parser.parse_args(sys.argv[1:])
	server_address = namespace.address
	server_port = namespace.port
	client_name = namespace.name

	# Проверяем номер порта
	if not 1023 < server_port < 65536:
		CLIENT_LOGGER.critical(
			f'Попытка запуска client с некоректным номером порта: {server_port}.'
			f'Адресс порта должен быть от 1024 до 65535. Программа завершена.'
		)
		sys.exit(1)

	return server_address, server_port, client_name


def main():
	'''
	Загружаем параметры командной строки
	server.py 127.0.0.1 8888 -n name
	'''
	server_address, server_port, client_name = arg_parser()

	"""Сообщаем о запуске"""
	print(f'Консольный месседжер. Клиентский модуль. Имя пользователя: {client_name}')

	# Если имя пользователя не было задано, необходимо запросить пользователя.
	if not client_name:
		client_name = input('Введите имя пользователя: ')

	CLIENT_LOGGER.info(
		f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
		f'порт: {server_port}, режим работы: {client_name}'
	)

	# Инициализируем сокет
	try:
		serv_sock = socket(AF_INET, SOCK_STREAM)
		serv_sock.connect((server_address, server_port))
		send_message(serv_sock, create_presence(client_name))
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
	except (ConnectionRefusedError, ConnectionError):
		CLIENT_LOGGER.critical(
			f'Не удалось подключиться к серверу {server_address}:{server_port}, '
			f'конечный компьютер отверг запрос на подключение.'
		)
		sys.exit(1)
	except NonDictInputError:
		CLIENT_LOGGER.error(f'Ответ сервера не является словарем')
		sys.exit(1)
	else:
		# Если соединение с сервером установлено корректно,
		# запускаем клиентский процесс приёма сообщений
		receiver = threading.Thread(target=message_from_server, args=(serv_sock, client_name))
		receiver.daemon = True
		receiver.start()

		# затем запускаем отправку сообщений и взаимодействие с пользователем.
		user_interface = threading.Thread(target=user_interactive, args=(serv_sock, client_name))
		user_interface.daemon = True
		user_interface.start()
		CLIENT_LOGGER.debug('Запущены процессы')

		# Watchdog основной цикл, если один из потоков завершён,
		# то значит или потеряно соединение или пользователь
		# ввёл exit. Поскольку все события обработываются в потоках,
		# достаточно просто завершить цикл.
		while True:
			time.sleep(1)
			if receiver.is_alive() and user_interface.is_alive():
				continue
			break


if __name__ == '__main__':
	main()
