import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
from common.variables import ENCODING, MAX_PACKAGE_LENGTH, ACTION, PRESENCE, \
    TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
import json
from common.utils import send_message, get_message


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):

    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 1.1,
        USER: {
            ACCOUNT_NAME: 'test_name'
        }
    }

    test_dict_recv_correct = {RESPONSE: 200}
    test_dict_recv_error = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_message_correct(self):
        test_socket_correct = TestSocket(self.test_dict_recv_correct)
        test_socket_error = TestSocket(self.test_dict_recv_error)
        self.assertEqual(get_message(test_socket_correct), self.test_dict_recv_correct)

    def test_get_message_error(self):
        test_socket_correct = TestSocket(self.test_dict_recv_correct)
        test_socket_error = TestSocket(self.test_dict_recv_error)
        self.assertEqual(get_message(test_socket_error), self.test_dict_recv_error)

    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_send_message_raise(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertRaises(TypeError, send_message, test_socket, "Неправильный словарь")


if __name__ == '__main__':
    unittest.main()
