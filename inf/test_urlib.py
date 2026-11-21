import urllib.parse

if __name__ == '__main__':
    word = input()
    print(f"You put the word - {word.upper()}")
    # заменяет специальные и кириллические символы в строке на их безопасное представление
    encoded_word = urllib.parse.quote(word)
    print(f"Encoded word - {encoded_word}")
