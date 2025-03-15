
def addition_bin(first, second):
    result = []
    next = 0
    MAX_LENGTH = 8
    for i in range(MAX_LENGTH - 1, -1, -1):
        count = first[i] + second[i] + next
        next = 0 if count < 2 else 1
        result.append(count % 2)
    result.reverse()
    return result
