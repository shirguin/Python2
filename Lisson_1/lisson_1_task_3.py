# Задание №3
# Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.

words = ['attribute', 'класс', 'функция', 'type']

for word in words:
    flag = True
    for symbol in word:
        if ord(symbol) > 127:
            flag = False
    if flag:
        word_byte = eval(f'b"{word}"')
        print(f'Слово: {word} в байтовом типе: {word_byte}')
    else:
        word_byte = word.encode('utf-8')
        print(f'Слово: {word} не возможно записать в байтовом типе без использования encode')
        print(f'Слово: {word} в байтовом типе: {word_byte}')


