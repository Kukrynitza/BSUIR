import math
from sorce.addition_bin import addition_bin
from sorce.to_bin import to_bin
from sorce.to_bin_for_subtraction import to_bin_for_subtraction
from sorce.twos_complement_to_decimal import twos_complement_to_decimal
from sorce.multiplication_bin import multiplication_bin
from sorce.division_bin import division_bin
from sorce.addition_float import addition_float
from sorce.float_to_ieee754 import float_to_ieee754


def binary_to_decimal(binary_list):
    list = binary_list[1:]
    decimal = 0
    length = len(list)

    for i in range(length):
        decimal += list[i] * (2 ** (length - 1 - i))
    if(binary_list[0] == 1):
        decimal = -decimal
    return decimal


def binary_to_decimal_str(binary_str):
    integer_part, fractional_part = binary_str.split('.')

    integer_value = sum(int(bit) * (2 ** (len(integer_part) - 1 - i)) for i, bit in enumerate(integer_part))

    fractional_value = sum(int(bit) * (2 ** -(i + 1)) for i, bit in enumerate(fractional_part))

    return integer_value + fractional_value

def ieee754_to_float(ieee):
    MAX_BIT_SIZE = 127
    EXPONENT_SIZE = 9
    BIT_LENGTH = 32
    TWO = 2
    exponent = 0
    for i in range(1, EXPONENT_SIZE):
        exponent = exponent * TWO + ieee[i]
    exponent -= MAX_BIT_SIZE

    mantissa = 1.0
    for i in range(EXPONENT_SIZE, BIT_LENGTH):
        mantissa += ieee[i] * (TWO ** (EXPONENT_SIZE - 1 - i))

    return mantissa * (TWO ** exponent)

def addition_float(first, second):
    first_ieee = float_to_ieee754(first)
    second_ieee = float_to_ieee754(second)

    result = first + second
    return float_to_ieee754(result)

def menu(choise):
    match choise:
        case 1:
            first_num = input('Введите первое число: ')
            first_bin_num = to_bin(int(first_num), 'additionally')

            second_num = input('Введите второе число: ')
            second_bin_num = to_bin(int(second_num), 'additionally')
            result = addition_bin(first_bin_num, second_bin_num)
            print(result)
            return twos_complement_to_decimal(result)
        case 2:
            first_num = input('Введите первое число: ')
            first_bin_num = to_bin(int(first_num), 'additionally')

            second_num = input('Введите второе число: ')
            second_bin_num = to_bin(int(second_num), 'additionally')
            second_bin_num = to_bin_for_subtraction(-int(second_num))

            result = addition_bin(first_bin_num, second_bin_num)
            print(result)
            return twos_complement_to_decimal(result)
        case 3:
            first_num = input('Введите первое число: ')
            first_bin_num = to_bin(int(first_num), 'additionally')

            second_num = input('Введите второе число: ')
            second_bin_num = to_bin(int(second_num), 'additionally')
            result = multiplication_bin(first_bin_num, second_bin_num)
            print(result)
            return binary_to_decimal(result)
        case 4:
            first_num = input('Введите первое число: ')
            first_bin_num = to_bin(int(first_num), 'direct')

            second_num = input('Введите второе число: ')
            second_bin_num = to_bin(int(second_num), 'direct')

            result = division_bin(first_bin_num, second_bin_num)
            print(result)
            return binary_to_decimal_str(result)
        case 5:
            first_num = float(input('Введите первое положительное число: '))
            second_num = float(input('Введите второе положительное число: '))
            if first_num < 0 or second_num < 0:
                return "Числа должны быть положительными"

            result_ieee = addition_float(first_num, second_num)
            print("Результат в IEEE-754:", result_ieee)
            return ieee754_to_float(result_ieee)
        case _:
            return 'Ошибка в выборе'


if __name__ == '__main__':
    choise = input('Введите название операции\n'
                   '1 - сложение в дополнительном коде\n'
                   '2 - вычитание в дополнительном коде\n'
                   '3 - умножение в прямом коде\n'
                   '4 - деление в прямом коде\n'
                   '5 - сложение чисел с плавающей точкой\n'
                   'Ввод: ')
    print(menu(int(choise)))
