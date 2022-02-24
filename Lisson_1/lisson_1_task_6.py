# Задание №6
# Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.


from chardet import detect

lines = ['сетевое программирование', 'сокет', 'декоратор']
file = open("test_file.txt", "w", encoding='utf-8')
for line in lines:
    file.write(line + '\n')
file.close()

with open("test_file.txt", 'rb') as file:
    content = file.read()
encoding = detect(content)['encoding']
print(f'Кодировка файла: {encoding}')


with open("test_file.txt", encoding=encoding) as file:
    for line in file:
        print(line, end='')
