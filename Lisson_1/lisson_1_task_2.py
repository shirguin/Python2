# Задание №2
# Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
# (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.

words = ['class', 'function', 'method']
words_byte = []

for word in words:
    words_byte.append(eval(f'b"{word}"'))

for word in words_byte:
    print(f'тип: {type(word)} длина: {len(word)} слово: {word}')
