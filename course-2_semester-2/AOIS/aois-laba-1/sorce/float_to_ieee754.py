def float_to_ieee754(num):
    SQUARE_ROOT = 2
    TRUE_BIT_SIZE = 7
    MANTIS_BIT_LENGTH = 23
    MAX_BIT_SIZE = 127
    result = [0]

    integer_part = int(num)
    fractional_part = num - integer_part

    binary = []
    if integer_part == 0:
        binary = ['0']
    while integer_part > 0:
        binary.insert(0, str(integer_part % SQUARE_ROOT))
        integer_part //= SQUARE_ROOT

    binary.append('.')
    for _ in range(MANTIS_BIT_LENGTH):
        fractional_part *= SQUARE_ROOT
        bit = int(fractional_part)
        binary.append(str(bit))
        fractional_part -= bit

    point_pos = binary.index('.')
    first_one_pos = ''.join(binary).replace('.', '').index('1')
    exponent = point_pos - first_one_pos - 1 + MAX_BIT_SIZE

    for i in range(TRUE_BIT_SIZE, -1, -1):
        result.append(1 if exponent & (1 << i) else 0)

    binary_str = ''.join(binary).replace('.', '')
    mantissa_start = first_one_pos + 1
    mantissa = binary_str[mantissa_start:mantissa_start + MANTIS_BIT_LENGTH]
    mantissa = mantissa.ljust(MANTIS_BIT_LENGTH, '0')
    result.extend([int(x) for x in mantissa])

    return result
