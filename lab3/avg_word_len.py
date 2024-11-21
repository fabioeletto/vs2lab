with open('lorem_ipsum.txt', mode='r', encoding='utf-8') as file:
    text = file.read()

paragraphs = text.split('.')

word_count = 0
char_count = 0

for p in paragraphs:

    words = p.split(' ')

    for w in words:
        word_count += 1
        char_count += len(w)

avg_word_len = char_count / word_count

print(f'words: {word_count} | chars: {char_count} | avg_word_len: {avg_word_len}')