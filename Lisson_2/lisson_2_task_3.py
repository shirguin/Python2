# Задание №3
# 3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий сохранение данных
# в файле YAML-формата. Для этого:
#   а. Подготовить данные для записи в виде словаря, в котором первому ключу соответствует список,
#       второму — целое число, третьему — вложенный словарь, где значение каждого ключа — это целое число с
#       юникод-символом, отсутствующим в кодировке ASCII (например, €);
#   b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml. При этом обеспечить стилизацию
#       файла с помощью параметра default_flow_style, а также установить возможность работы с юникодом:
#       allow_unicode = True;
#   c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.

import yaml
from yaml.loader import SafeLoader
from pprint import pprint


def write_data_to_yaml(file_name, dict_data):
    with open(file_name, 'w', encoding='utf-8') as f:
        yaml.dump(dict_data, f, default_flow_style=False, allow_unicode=True, indent=4)


def read_data_from_yaml(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = yaml.load(f, Loader=SafeLoader)
            return content
    except FileNotFoundError:
        print('Указанный файл не найден.')


data = {
    'key_1': [10, 20, 30, 40],
    'key_2': 10800,
    'key_3': {
        '1€': 'Одно евро',
        '2€': 'Два евро',
        '15€': 'Пятнадцать евро'
    }
}

file = 'file.yaml'
write_data_to_yaml(file, data)

data_1 = read_data_from_yaml(file)

if data == data_1:
    print('Все работает правильно!!!')
else:
    print('Беда!!!')

pprint(data_1)
