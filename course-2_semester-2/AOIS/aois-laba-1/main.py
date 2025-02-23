import math


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

def addition_bin(first, second):
    result = []
    next = 0
    max_length = 8
    for i in range(max_length - 1, -1, -1):
        count = first[i] + second[i] + next
        next = 0 if count < 2 else 1
        result.append(count % 2)
    result.reverse()
    return result
def to_bin(num, choise):
    direct = []
    if(num >= 0):
        direct.append(0)
    else:
        direct.append(1)
    while num != 0:
        direct.insert(-1, num % 2)
        num = math.trunc(num / 2)
    direct.reverse()
    if len(direct) < 8:
            direct = direct[:1] + [0] * (8 - len(direct)) + direct[1:]
    print('В прямом коде:', direct)
    inverse = []
    additionally = []
    if(direct[0] == 0):
        inverse = direct
        additionally = direct
    else:
        inverse.append(1)
        for element in direct[1:]:
            inverse.append(0 if element == 1 else 1)
        additionally = addition_bin(inverse, [0, 0, 0, 0, 0, 0, 0, 1])
    print('В обратном', inverse)
    print('В дополнителльном', additionally)
    if(choise == 'direct'):
        return direct
    if(choise == 'inverse'):
        return inverse
    if(choise == 'additionally'):
        return additionally

def to_bin_for_subtraction(num):
    direct = []
    if(num >= 0):
        direct.append(0)
    else:
        direct.append(1)
    while num != 0:
        direct.insert(-1, num % 2)
        num = math.trunc(num / 2)
    direct.reverse()
    if len(direct) < 8:
            direct = direct[:1] + [0] * (8 - len(direct)) + direct[1:]
    inverse = []
    additionally = []
    if(direct[0] == 0):
        inverse = direct
        additionally = direct
    else:
        inverse.append(1)
        for element in direct[1:]:
            inverse.append(0 if element == 1 else 1)
        additionally = addition_bin(inverse, [0, 0, 0, 0, 0, 0, 0, 1])
    return additionally
def compare_binary(a, b):
    while len(a) > 1 and a[0] == 0:
        a.pop(0)
    while len(b) > 1 and b[0] == 0:
        b.pop(0)

    if len(a) != len(b):
        return len(a) > len(b)
    return a >= b

def subtract_binary(a, b):
    a = a[:]
    b = [0] * (len(a) - len(b)) + b
    borrow = 0

    for i in range(len(a) - 1, -1, -1):
        a[i] = a[i] - b[i] - borrow
        if a[i] < 0:
            a[i] += 2
            borrow = 1
        else:
            borrow = 0

    while len(a) > 1 and a[0] == 0:
        a.pop(0)

    return a if a else [0]

def division_bin(dividend, divisor):
    if all(bit == 0 for bit in divisor):
        return "Ошибка: Деление на ноль"

    sign = '-' if (dividend[0] != divisor[0]) else ''

    abs_dividend = dividend[1:]
    abs_divisor = divisor[1:]

    quotient = []
    remainder = []

    for bit in abs_dividend:
        remainder.append(bit)
        if compare_binary(remainder, abs_divisor):
            quotient.append(1)
            remainder = subtract_binary(remainder, abs_divisor)
        else:
            quotient.append(0)

    while len(quotient) > 1 and quotient[0] == 0:
        quotient.pop(0)

    quotient.append('.')
    fractional_part = []

    for _ in range(5):
        remainder.append(0)
        if compare_binary(remainder, abs_divisor):
            fractional_part.append(1)
            remainder = subtract_binary(remainder, abs_divisor)
        else:
            fractional_part.append(0)

    result = sign + ''.join(map(str, quotient)) + ''.join(map(str, fractional_part))
    return result
def multiplication_bin(first_num, second_num):
    sign = 0 if first_num[0] == second_num[0] else 1
    result = [0,0,0,0,0,0,0,0]
    for i in range(7, 0, -1):
        if(second_num[i] == 0):
            continue
        first = [0] + first_num[1:]
        first = first[(7 - i):] + [0] * (7 - i)
        result = addition_bin(result, first)
    return [sign] + result[1:]
def float_to_ieee754(num):
    result = [0]

    integer_part = int(num)
    fractional_part = num - integer_part

    binary = []
    if integer_part == 0:
        binary = ['0']
    while integer_part > 0:
        binary.insert(0, str(integer_part % 2))
        integer_part //= 2

    binary.append('.')
    for _ in range(23):
        fractional_part *= 2
        bit = int(fractional_part)
        binary.append(str(bit))
        fractional_part -= bit

    point_pos = binary.index('.')
    first_one_pos = ''.join(binary).replace('.', '').index('1')
    exponent = point_pos - first_one_pos - 1 + 127

    for i in range(7, -1, -1):
        result.append(1 if exponent & (1 << i) else 0)

    binary_str = ''.join(binary).replace('.', '')
    mantissa_start = first_one_pos + 1
    mantissa = binary_str[mantissa_start:mantissa_start + 23]
    mantissa = mantissa.ljust(23, '0')
    result.extend([int(x) for x in mantissa])

    return result


def ieee754_to_float(ieee):
    exponent = 0
    for i in range(1, 9):
        exponent = exponent * 2 + ieee[i]
    exponent -= 127

    mantissa = 1.0
    for i in range(9, 32):
        mantissa += ieee[i] * (2 ** (8 - i))

    return mantissa * (2 ** exponent)
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
            return binary_to_decimal(result)
        case 2:
            first_num = input('Введите первое число: ')
            first_bin_num = to_bin(int(first_num), 'additionally')

            second_num = input('Введите второе число: ')
            second_bin_num = to_bin(int(second_num), 'additionally')
            second_bin_num = to_bin_for_subtraction(-int(second_num))

            result = addition_bin(first_bin_num, second_bin_num)
            print(result)
            return binary_to_decimal(result)
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
    choise = input('Введите название опрерации\n'
                   '1 - сложение в дополнительном коде\n'
                   '2 - вычитание в дополнительном коде\n'
                   '3 - умножение в прямом коде\n'
                   '4 - деление в прямом коде\n'
                   '5 - сложение чисел с плавающей точкой\n'
                   'Ввод: ')
    print(menu(int(choise)))