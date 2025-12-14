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
    FIVE_RANGE = 5
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

    for _ in range(FIVE_RANGE):
        remainder.append(0)
        if compare_binary(remainder, abs_divisor):
            fractional_part.append(1)
            remainder = subtract_binary(remainder, abs_divisor)
        else:
            fractional_part.append(0)

    result = sign + ''.join(map(str, quotient)) + ''.join(map(str, fractional_part))
    return result
