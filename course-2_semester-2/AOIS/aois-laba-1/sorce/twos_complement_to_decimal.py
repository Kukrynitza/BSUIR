def twos_complement_to_decimal(bits):
    BIT_LENGTH = 8
    ORIGIN_BIT_LENGTH = 7
    if len(bits) != BIT_LENGTH:
        raise ValueError("Массив должен содержать ровно 8 элементов")

    if bits[0] == 1:
        inverted_bits = [1 - bit for bit in bits]
        carry = 1
        for i in range(ORIGIN_BIT_LENGTH, -1, -1):
            if inverted_bits[i] == 1 and carry == 1:
                inverted_bits[i] = 0
            elif inverted_bits[i] == 0 and carry == 1:
                inverted_bits[i] = 1
                carry = 0
        value = -sum(inverted_bits[i] * (2 ** (ORIGIN_BIT_LENGTH - i)) for i in range(BIT_LENGTH))
    else:
        value = sum(bits[i] * (2 ** (ORIGIN_BIT_LENGTH - i)) for i in range(BIT_LENGTH))

    return value
