from sorce.addition_bin import addition_bin

def multiplication_bin(first_num, second_num):
    TRUE_BIT_SIZE = 7
    sign = 0 if first_num[0] == second_num[0] else 1
    result = [0,0,0,0,0,0,0,0]
    for i in range(TRUE_BIT_SIZE, 0, -1):
        if(second_num[i] == 0):
            continue
        first = [0] + first_num[1:]
        first = first[(TRUE_BIT_SIZE - i):] + [0] * (TRUE_BIT_SIZE - i)
        result = addition_bin(result, first)
    return [sign] + result[1:]