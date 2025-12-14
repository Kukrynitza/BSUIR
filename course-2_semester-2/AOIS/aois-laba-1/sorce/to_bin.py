import math
from sorce.addition_bin import addition_bin

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
