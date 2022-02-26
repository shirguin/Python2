# Задание №1
# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных
# из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
#     а. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие
#       и считывание данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь
#       значения параметров «Изготовитель системы»,  «Название ОС», «Код продукта», «Тип системы». Значения каждого
#       параметра поместить в соответствующий список. Должно получиться четыре списка — например,
#       os_prod_list, os_name_list, os_code_list, os_type_list. В этой же функции создать главный список для хранения
#       данных отчета — например, main_data — и поместить в него названия столбцов отчета в виде списка:
#       «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих столбцов также
#       оформить в виде списка и поместить в файл main_data (также для каждого файла);
#     b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
#       данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
#     c. Проверить работу программы через вызов функции write_to_csv().

import csv
import re
from chardet import detect


def get_encoding(file):
    with open(file, 'rb') as f:
        content = f.read()
        encoding = detect(content)['encoding']
    return encoding


def get_data(ls_data):
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]

    for file in ls_data:
        with open(file, encoding=get_encoding(file)) as data_file:
            for line in data_file:
                if re.match('Изготовитель системы', line):
                    os_prod_list.append(re.search(r'(Изготовитель системы).\s*(.*)', line).group(2))
                elif re.match('Название ОС', line):
                    os_name_list.append(re.search(r'(Название ОС).\s*(.*)', line).group(2))
                elif re.match('Код продукта', line):
                    os_code_list.append(re.search(r'(Код продукта).\s*(.*)', line).group(2))
                elif re.match('Тип системы', line):
                    os_type_list.append(re.search(r'(Тип системы).\s*(.*)', line).group(2))

    i = 0
    while i < len(ls_data):
        main_data.append([
            os_prod_list[i],
            os_name_list[i],
            os_code_list[i],
            os_type_list[i],
        ])
        i += 1
    return main_data


def write_to_csv(file_name_, ls_data_files_):
    data = get_data(ls_data_files_)
    with open(file_name_, 'w', encoding='utf-8', newline='') as file:
        file_writer = csv.writer(file)
        file_writer.writerows(data)


def read_and_show_csv(file_csv):
    with open(file_csv, encoding='utf-8') as file:
        file_reader = csv.reader(file)
        for row in file_reader:
            print(row)


ls_data_files = ["info_1.txt", 'info_2.txt', 'info_3.txt']
file_name = 'summary_report.csv'

write_to_csv(file_name, ls_data_files)
read_and_show_csv(file_name)
