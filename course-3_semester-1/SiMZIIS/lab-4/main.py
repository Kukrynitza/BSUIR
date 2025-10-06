import random

def mod_exp(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent = exponent >> 1
    return result

def is_primitive(g, p):
    powers = set()
    current = g
    for i in range(1, p):
        powers.add(current)
        if len(powers) != i or current == 0:
            return False
        current = (current * g) % p
    return len(powers) == p - 1

def find_primitive(p):
    for g in range(2, p):
        if is_primitive(g, p):
            return g
    return None

P = 7237
g = find_primitive(P)

a = random.randint(2, P - 2)
b = random.randint(2, P - 2)

A = mod_exp(g, a, P)
B = mod_exp(g, b, P)

secret_bob = mod_exp(B, a, P)
secret_alice = mod_exp(A, b, P)

print(f"P = {P}")
print(f"g = {g}")
print(f"Секретный ключ bob = {a}")
print(f"Секретный ключ alice = {b}")
print(f"Публичный ключ bob = {A}")
print(f"Публичный ключ alice = {B}")
print(f"Общий секрет bob = {secret_bob}")
print(f"Общий секрет Bob = {secret_alice}")
print(secret_bob == secret_alice)