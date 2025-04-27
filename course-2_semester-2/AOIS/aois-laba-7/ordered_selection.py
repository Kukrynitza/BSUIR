# === Глобальные переменные ===
G_EXPR = "G|(!A&B&!L)"
L_EXPR = "L|(A&!B&!G)"

truth_table = {
    'combinations': [],
    'statements': {},
    'basic_logic_expressions': []
}

matrix = None  # Твоя матрица

# === Функции ===

def init(matrix_input):
    global matrix, truth_table
    matrix = matrix_input
    combinations = [[] for _ in range(matrix_size())]
    combinations[0].append(0)
    combinations[0].append(0)
    truth_table['combinations'] = combinations

def matrix_size():
    return len(matrix)

def get_word(index):
    return matrix[index]

def write_word(index, word):
    matrix[index] = word

def parse_on_basic_expressions(expr, statements):
    expr = expr.replace('!', ' not ')
    expr = expr.replace('&', ' and ')
    expr = expr.replace('|', ' or ')
    return expr

def create_line(current_iteration):
    combinations = truth_table['combinations']
    values = combinations[current_iteration][:2]  # A и B
    A = values[0]
    B = values[1]
    G = combinations[current_iteration][2] if len(combinations[current_iteration]) > 2 else 0
    L = combinations[current_iteration][3] if len(combinations[current_iteration]) > 3 else 0

    expr = truth_table['basic_logic_expressions']

    result = eval(expr, {}, {"A": bool(A), "B": bool(B), "G": bool(G), "L": bool(L)})

    combinations[current_iteration].append(int(result))

def compare(A, S, current_iteration):
    combinations = truth_table['combinations']
    traverse = current_iteration

    if len(combinations[traverse]) > 2:
        while combinations[traverse]:
            combinations[traverse].clear()
            if traverse != 15:
                traverse += 1
            else:
                break
        if current_iteration == 0:
            combinations[current_iteration].append(0)
            combinations[current_iteration].append(0)

    combinations[current_iteration].insert(0, S[current_iteration])
    combinations[current_iteration].insert(0, A[current_iteration])

    truth_table['statements'] = {}
    truth_table['basic_logic_expressions'] = parse_on_basic_expressions(L_EXPR, truth_table['statements'])
    create_line(current_iteration)

    L0 = combinations[current_iteration][-1]
    if current_iteration != 15:
        combinations[current_iteration + 1].append(L0)

    while len(combinations[current_iteration]) > 4:
        combinations[current_iteration].pop()

    truth_table['statements'] = {}
    truth_table['basic_logic_expressions'] = parse_on_basic_expressions(G_EXPR, truth_table['statements'])
    create_line(current_iteration)

    G0 = combinations[current_iteration][-1]

    if L0 == 1 and G0 == 0:
        return 1
    elif G0 == 1 and L0 == 0:
        return -1

    if current_iteration != 15:
        combinations[current_iteration + 1].append(G0)
        while len(combinations[current_iteration]) > 4:
            combinations[current_iteration].pop()
        return compare(A, S, current_iteration + 1)

    while len(combinations[current_iteration]) > 4:
        combinations[current_iteration].pop()

    return 0

def find_max(num, last):
    for i in range(last):
        if compare(get_word(num), get_word(i), 0) < 0:
            return i
    return num

def sort_matrix():
    for last in range(matrix_size() - 1, -1, -1):
        max_index = last
        max_last = -1
        while max_last != max_index:
            max_last = max_index
            max_index = find_max(max_last, last)

        word_to_swap = get_word(last)
        write_word(last, get_word(max_index))
        write_word(max_index, word_to_swap)

def ordered_selection(matrix_data):
    print("Матрица до сортировки:")
    for row in matrix_data:
        print(row)

    init(matrix_data)
    sort_matrix()

    print("\nМатрица после сортировки:")
    for row in matrix_data:
        print(row)
    return matrix_data