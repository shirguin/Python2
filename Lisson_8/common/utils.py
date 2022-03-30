"""Утилиты"""

from common.variables import MAX_PACKAGE_LENGTH, ENCODING
import json
from decorators.decors_def import log


# Принимает и декодирует сообщение, возвращает словарь
@log
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


# Кодирует и отправляет сообщение
@log
def send_message(sock, message):
    if not isinstance(message, dict):
        raise TypeError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    sock.send(encoded_message)
