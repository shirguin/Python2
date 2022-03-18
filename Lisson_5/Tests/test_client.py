# from pprint import pprint
import sys
# pprint(sys.path)
sys.path.append('../') # Выбрал вариант покороче
# pprint(sys.path)
# import os
# sys.path.append(os.path.join(os.getcwd(), '..'))
# pprint(sys.path)
import unittest
from client import create_presence, process_server_answer
from common.variables import USER, ACCOUNT_NAME, ACTION, TIME, PRESENCE, ERROR, RESPONSE


class TestCreatePresence(unittest.TestCase):

    def setUp(self):
        # print('Начало теста')
        pass

    def tearDown(self):
        # print('Конец теста')
        pass

    def test_create_presence_default_account_name(self):
        self.assertEqual(create_presence()[USER][ACCOUNT_NAME], 'Guest',
                         'Не праильно назначено default_name')

    def test_create_presence_account_name(self):
        self.assertEqual(create_presence('Alex')[USER][ACCOUNT_NAME], 'Alex',
                         'Не правильно назначено account_name !!!')

    def test_create_presence_action(self):
        self.assertEqual(create_presence()[ACTION], 'presence',
                         'Не правильное значение action в словаре !!!')

    def test_create_presence_time(self):
        test = create_presence()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}},
                         'Не правильное значение time !!!')


class TestProcessServerAnswer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_process_server_answer_200(self):
        test_message = {RESPONSE: 200}
        self.assertEqual(process_server_answer(test_message), '200 : OK', 'Не верный ответ на код 200')

    def test_process_server_answer_400(self):
        test_message = {RESPONSE: 400,
                        ERROR: 'Bad Request'
                        }
        self.assertEqual(process_server_answer(test_message), f'400 : {test_message[ERROR]}',
                         'Не верный ответ на код отличный от 200')

    def test_process_server_answer_no_response(self):
        self.assertRaises(ValueError, process_server_answer, {ERROR: 'Bad Request'})


if __name__ == "__main__":
    unittest.main()

