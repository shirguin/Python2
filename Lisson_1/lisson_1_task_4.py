# Задание №4
# Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
# в байтовое и выполнить обратное преобразование (используя методы encode и decode).

words = ['разработка', 'администрирование', 'protocol', 'standard']
words_byte = []
for word in words:
    words_byte.append(word.encode('utf-8'))
print(words_byte)

words_1 = []
for word in words_byte:
    words_1.append(word.decode('utf-8'))

print(words_1)
