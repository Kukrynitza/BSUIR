from sorce.float_to_ieee754 import float_to_ieee754

def addition_float(first, second):
    first_ieee = float_to_ieee754(first)
    second_ieee = float_to_ieee754(second)

    result = first + second
    return float_to_ieee754(result)