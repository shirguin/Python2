# Задание №2
# 2.Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
# Написать скрипт, автоматизирующий его заполнение данными. Для этого:
#   a.Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
#       цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря в
#       файл orders.json. При записи данных указать величину отступа в 4 пробельных символа;
#   b.Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого
#       параметра.

import json
from pprint import pprint


def get_orders(file_orders):
    with open(file_orders, encoding='utf-8') as f:
        orders = json.load(f)
        return orders


def create_order(values):
    keys = ['item', 'quantity', 'price', 'buyer', 'date']
    return dict(zip(keys, values))


def write_order_to_json(file_orders, values):
    obj = get_orders(file_orders)
    obj['orders'].append(create_order(values))
    with open(file_orders, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=4, sort_keys=True, ensure_ascii=False)


def read_order_of_json(file_orders, number):
    obj = get_orders(file_orders)
    if number in range(len(obj['orders'])):
        return obj['orders'][number]
    else:
        return None


file_name = 'orders.json'
values_order = ['Ручка шариковая BIG', 3, 25, 'Иванов Иван Иванович', '26.02.22']

print('Начальные условия:')
pprint(get_orders(file_name))

print('Добавление заказа в файл:')
write_order_to_json(file_name, values_order)
pprint(get_orders(file_name))

print('Проверяем работу программы:')
order_1 = create_order(values_order)
order_2 = read_order_of_json(file_name, 0)

if order_1 == order_2:
    print('Все работает правильно!!!')
else:
    print('Беда!!')

print('Добавление следующего заказа в файл:')
values_order_1 = ['Карандаш', 10, 15, 'Семенов Иван Иванович', '01.02.22']
write_order_to_json(file_name, values_order_1)
pprint(get_orders(file_name))
