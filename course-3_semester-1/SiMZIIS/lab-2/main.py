import random
import string
import time
def generate_matrix():
    all_letters = string.ascii_letters
    random_letters_column = [random.choice(all_letters) for _ in range(column)]
    random_letters_string = [random.choice(all_letters) for _ in range(line)]
    matrix = random_letters_string.copy()
    for element in range(len(matrix)):
        matrix[element] = random_letters_column.copy()
    return matrix

def text_encryption(matrix, line, column, text):
    for letters_string in range(line):
        for letters_column in range(column):
            try:
                matrix[letters_string][letters_column] = text[(column * letters_string) + letters_column]
            except:
                break
    print(matrix)
    encryption: str = ''
    for letters_column in range(column):
        for letters_string in range(line):
            encryption += matrix[letters_string][letters_column]
    return encryption

def clear_text_decryption(encryption, line, column, text_len):
    decryption: str = ''
    clear_decryption: str = ''
    for letters_string in range(line):
        for letters_column in range(column):
            decryption += encryption[(letters_column * line) + letters_string]
    clear_decryption = decryption[:text_len]
    return decryption, clear_decryption

def text_decryption(encryption, line, column):
    decryption: str = ''
    for letters_string in range(line):
        for letters_column in range(column):
            try:
                decryption += encryption[(letters_column * line) + letters_string]
            except:
                continue
    return decryption

def key_selection_brud_force(encryption, decryption, max, min):
    for column in range(max):
        for line in range(max):
            if column <= min and line <= min:
                continue
            test_decryption = text_decryption(encryption, line, column)
            if test_decryption == decryption:
                end_time = time.time()
                return end_time
    return None

def key_selection(encryption, decryption):
    MAX = 130
    start_time = time.time()
    end_time = None
    for element in range(MAX):
        end_time = key_selection_brud_force(encryption, decryption, element + 2, element)
        if end_time != None:
            break

    if end_time != None:
        elapsed_time = end_time - start_time
        print(f'Ключи были подобраны за {elapsed_time} секунд')
    else:
        print(f'Ключи не были подобраны, число операций превышает 6400')


if __name__ == '__main__':
    while True:
        text: str
        column: int
        line: int
        try:
            # text: str = input('Введите текст: ')
            text = 'QWERTY'
            column: int = int(input('Количество столбцов:'))
            line: int = int(input('Количество строк:'))
        except:
            print('Неправильно введены значения')
            break
        if len(text) > column * line:
            print('Длина текста больше произведения столбцов на строки')
            break
        matrix = generate_matrix()
        encryption = text_encryption(matrix, line, column, text)
        decryption, clear_decryption = clear_text_decryption(encryption, line, column, len(text))
        print(f'Оригинальный текст: {text}')
        print(f'Зашифрованный текст: {encryption}')
        print(f'Расшифрованный текст: {decryption} (с лишними символами); {clear_decryption} (без лишних символов)')
        key_selection(encryption, decryption)
        break