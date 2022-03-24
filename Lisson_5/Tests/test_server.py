import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
from server import process_client_message
from common.variables import RESPONSE, ERROR, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME


class TestProcessClientMessage(unittest.TestCase):
    correct_dict = {RESPONSE: 200}
    error_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_process_client_message_ok_check(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.correct_dict, 'Ошибка при корректном запросе !!!')

    def test_process_client_message_no_action(self):
        self.assertEqual(process_client_message({TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.error_dict, 'Ошибка нет action !!!')

    def test_process_client_message_no_correct_action(self):
        self.assertEqual(process_client_message({ACTION: 'Test', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.error_dict, 'Ошибка при неизвестном action !!!')

    def test_process_client_message_no_time(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.error_dict, 'Ошибка при отсутствии TIME !!!')

    def test_process_client_message_no_user(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1}),
                         self.error_dict, 'Ошибка при отсутствии USER !!!')

    def test_process_client_message_unknown_user(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'test'}}),
                         self.error_dict, 'Ошибка при неизвестном USER !!!')


if __name__ == "__main__":
    unittest.main()
