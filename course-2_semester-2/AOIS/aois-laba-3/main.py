import math
import string


def process_expression(expression):
    def get_operator_priority(operator):
        priorities = {
            '!': 4,
            '&': 3,
            '|': 2,
            '->': 1,
            '~': 1,
            '(': 0
        }
        return priorities.get(operator, 0)

    def infix_to_rpn(expr):
        output = []
        operator_stack = []
        i = 0

        while i < len(expr):
            if expr[i].isspace():
                i += 1
                continue

            if expr[i] in 'abcde':
                output.append(expr[i])
                i += 1
                continue

            if expr[i] == '!' and i + 1 < len(expr) and expr[i + 1] in 'abcde':
                output.append(f"!{expr[i + 1]}")
                i += 2
                continue

            if expr[i] == '(':
                operator_stack.append('(')
                i += 1
                continue

            if expr[i] == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                i += 1
                continue

            if expr[i] in '&|!->~':
                current_op = expr[i]
                if current_op == '-' and i + 1 < len(expr) and expr[i + 1] == '>':
                    current_op = '->'
                    i += 1

                while (operator_stack and operator_stack[-1] != '(' and
                       get_operator_priority(operator_stack[-1]) >= get_operator_priority(current_op)):
                    output.append(operator_stack.pop())

                operator_stack.append(current_op)
                i += 1
                continue

            i += 1

        while operator_stack:
            if operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            else:
                operator_stack.pop()

        return output

    rpn_tokens = infix_to_rpn(expression)
    vars = [x for x in rpn_tokens if x[0] in 'abcde' or (len(x) > 1 and x[0] == '!' and x[1] in 'abcde')]

    return vars, rpn_tokens


def to_bin(num, length):
    direct = []
    while num != 0:
        direct.insert(0, num % 2)
        num = math.trunc(num / 2)
    while len(direct) < length:
        direct.insert(0, 0)

    return direct


def make_operation(first: int, second: int, operation: string):
    if operation == '&':
        if first == 1 and second == 1:
            return 1
        return 0
    elif operation == '|':
        if first == 0 and second == 0:
            return 0
        return 1
    elif operation == '->':
        if first == 1 and second == 0:
            return 0
        return 1
    elif operation == '~':
        if first == second:
            return 1
        return 0
    else:
        return 0


def table_create(exp: string, rpn: [], vars: []):
    vars_in_degree: int = 2 ** len(vars)
    vars_string: string = ''
    for i in vars:
        vars_string += i + ' '
    vars_string += '' + exp
    print(vars_string)
    index_form: [int] = []
    pdnf_exp_list: str = ''
    pcnf_exp_list: str = ''
    pdnf_list: [int] = []
    pcnf_list: [int] = []
    for i in range(vars_in_degree):
        bool_vars = to_bin(i, len(vars))
        str_numbers = [str(n) for n in bool_vars]
        bool_rpn: [string] = rpn.copy()
        for f in range(len(vars)):
            index = bool_rpn.index(vars[f])
            if '!' in vars[f]:
                if (bool_vars[f] == 0):
                    bool_rpn[index] = 1
                else:
                    bool_rpn[index] = 0
            else:
                bool_rpn[index] = bool_vars[f]
        check_info = rpn_check(bool_rpn)
        index_form.append(str(check_info))
        bool_vars_string = ' '.join(str_numbers) + '  ' + str(check_info)
        result_exp = ''
        for f in range(len(vars)):
            if '!' in vars[f] and bool_vars[f] == 0:
                continue
            elif '!' in vars[f] and bool_vars[f] == 1:
                result_exp += str(vars[f][1])
                print
            elif bool_vars[f] == 0:
                result_exp += '!' + str(vars[f])
            else:
                result_exp += str(vars[f])
            if check_info == 1:
                result_exp += '&'
            else:
                result_exp += '|'
        if check_info == 1:
            pdnf_list.append(i)
            pdnf_exp_list += '(' + result_exp + ')|'

        else:
            pcnf_list.append(i)
            pcnf_exp_list += '(' + result_exp + ')&'
        # print(bool_rpn)
        print(bool_vars_string)
    if len(pdnf_exp_list) != 0:
        pdnf_exp_list = pdnf_exp_list[:-1]
    if len(pcnf_exp_list) != 0:
        pcnf_exp_list = pcnf_exp_list[:-1]
    return {'index': ''.join(index_form), 'pdnf': pdnf_list, 'pcnf': pcnf_list, 'pdnf_exp_list': pdnf_exp_list,
            'pcnf_exp_list': pcnf_exp_list}


def rpn_check(rpn):
    vars: [string] = []
    for element in range(len(rpn)):
        if rpn[element] == 0 or rpn[element] == 1:
            vars.append(rpn[element])
            continue
        if rpn[element] == '!':
            if vars[-1] == 0:
                vars[-1] = 1
            else:
                vars[-1] = 0
        else:
            el: int = make_operation(vars[-1], vars[-2], rpn[element])
            vars.pop()
            vars.pop()
            vars.append(el)
    return vars[0]


def get_binary_terms(numbers, vars_count):
    """Преобразует числа в двоичные термы"""
    terms = []
    for num in numbers:
        binary = bin(num)[2:].zfill(vars_count)
        terms.append(binary)
    return terms


def can_glue_terms(term1, term2):
    """Проверяет, можно ли склеить два терма"""
    differences = 0
    pos = -1
    for i in range(len(term1)):
        if term1[i] != term2[i]:
            differences += 1
            pos = i
        if differences > 1:
            return False, -1
    return differences == 1, pos

def minimize_normal_form(numbers, vars_count, form_type="СДНФ"):
    if not numbers:
        return [], ""

    print(f"\nМинимизация {form_type}:")
    terms = get_binary_terms(numbers, vars_count)
    print(f"Исходные термы: {terms}")

    current_terms = terms
    iteration = 1

    while True:
        new_terms = glue_terms(current_terms, vars_count)
        print(f"Результат {iteration}-го склеивания: {new_terms}")

        if set(new_terms) == set(current_terms):
            break

        current_terms = new_terms
        iteration += 1

    expressions = []
    for term in current_terms:
        expr = term_to_expression(term, ['a', 'b', 'c'], form_type)
        if expr:
            expressions.append(expr)

    final_expression = ' | ' if form_type == "СДНФ" else ' & '
    final_expression = final_expression.join(expressions)

    return current_terms, final_expression


def glue_terms(terms, vars_count):
    """Выполняет склеивание термов, учитывая разницу в одной позиции"""
    result = set()
    used = set()

    print(f"\n[DEBUG] Входные термы для склеивания: {terms}")

    for i in range(len(terms)):
        for j in range(i + 1, len(terms)):
            can_glue, pos = can_glue_terms(terms[i], terms[j])
            if can_glue:
                used.add(terms[i])
                used.add(terms[j])
                glued = list(terms[i])
                glued[pos] = '-'
                result.add(''.join(glued))

    if not result or result == set(terms):  # Если новых термов нет или они не изменились, прерываем
        print("[DEBUG] Склеивание завершено, новых термов нет")
        return sorted(terms), True  # Добавляем флаг завершения

    print(f"[DEBUG] Склеенные термы: {sorted(result)}")

    for term in terms:
        if term not in used:
            result.add(term)

    print(f"[DEBUG] Итоговые термы после склеивания: {sorted(result)}")
    return sorted(result), False  # Указываем, что изменения были


def term_to_expression(term, variables, form_type="СДНФ"):
    result = []
    for i, (bit, var) in enumerate(zip(term, variables)):
        if bit == '1':
            result.append(var)
        elif bit == '0':
            result.append(f"!{var}")

    return (' & ' if form_type == "СДНФ" else ' | ').join(result) if result else ''


def find_essential_implicants(terms, original_terms):
    """Поиск существенных импликант с финальной проверкой покрытия"""
    table = {term: set() for term in terms}
    for term in terms:
        for original in original_terms:
            if all(tc == oc or tc == '-' for tc, oc in zip(term, original)):
                table[term].add(original)

    essential_implicants = set()
    covered_terms = set()
    remaining_terms = set(original_terms)

    print(f"[DEBUG] Начальная таблица покрытия: {table}")

    while remaining_terms and table:
        best_term = max(table, key=lambda t: len(table[t] & remaining_terms), default=None)
        if best_term is None:
            break
        essential_implicants.add(best_term)
        covered_terms.update(table[best_term])
        remaining_terms -= table[best_term]
        del table[best_term]

    # Проверяем, что все исходные термы покрыты
    if remaining_terms:
        essential_implicants.update(remaining_terms)

    print(f"[DEBUG] Существенные импликанты: {essential_implicants}")
    return list(essential_implicants)


def minimize_dnf_calculation(terms, vars_count):
    """Минимизация СДНФ методом Квайна-МакКласки с покрытием импликант"""
    if not terms:
        return [], ""

    print(f"\nМинимизация СДНФ:")
    print(f"Исходные термы: {terms}")

    current_terms = set(terms)
    previous_terms = set()

    while True:
        new_terms, no_changes = glue_terms(list(current_terms), vars_count)
        if no_changes or new_terms == current_terms or new_terms == previous_terms:
            print("[DEBUG] Минимизация завершена, термы не изменяются")
            break  # Прерываем цикл при отсутствии изменений
        previous_terms = set(current_terms)
        current_terms = set(new_terms)

    essential_implicants = find_essential_implicants(current_terms, terms)
    expressions = [term_to_expression(term, ['a', 'b', 'c'], "СДНФ") for term in essential_implicants if term]
    print(f"[DEBUG] Минимизированная ДНФ: {' | '.join(expressions)}")
    return essential_implicants, " | ".join(expressions)


def minimize_cnf_calculation(terms, vars_count):
    """Минимизация СКНФ методом Квайна-МакКласки с покрытием импликант"""
    if not terms:
        return [], ""

    print(f"\nМинимизация СКНФ:")
    print(f"Исходные термы: {terms}")

    current_terms = set(terms)
    previous_terms = set()

    while True:
        new_terms, no_changes = glue_terms(list(current_terms), vars_count)
        if no_changes or new_terms == current_terms or new_terms == previous_terms:
            print("[DEBUG] Минимизация завершена, термы не изменяются")
            break  # Прерываем цикл при отсутствии изменений
        previous_terms = set(current_terms)
        current_terms = set(new_terms)

    essential_implicants = find_essential_implicants(current_terms, terms)
    expressions = [term_to_expression(term, ['a', 'b', 'c'], "СКНФ") for term in essential_implicants if term]
    print(f"[DEBUG] Минимизированная КНФ: {' & '.join(expressions)}")
    return essential_implicants, " & ".join(expressions)


def minimize_dnf_calculation_table(terms, vars_count):
    print("\nМинимизация СДНФ расчетно-табличным методом:")
    print("Исходные термы:", terms)

    iteration = 1
    current_terms = set(terms)
    prime_implicants = set()

    while True:
        print(f"\nШаг склеивания {iteration}:")
        new_terms = set()
        used_terms = set()

        terms_list = list(current_terms)
        for i in range(len(terms_list)):
            for j in range(i + 1, len(terms_list)):
                term1 = terms_list[i]
                term2 = terms_list[j]

                diff_pos = -1
                diff_count = 0
                for pos in range(len(term1)):
                    if term1[pos] != term2[pos]:
                        diff_count += 1
                        diff_pos = pos
                        if diff_count > 1:
                            break

                if diff_count == 1:
                    new_term = list(term1)
                    new_term[diff_pos] = '-'
                    new_term = ''.join(new_term)
                    new_terms.add(new_term)
                    used_terms.add(term1)
                    used_terms.add(term2)
                    print(f"Склеиваем {term1} и {term2} → {new_term}")

        for term in current_terms:
            if term not in used_terms:
                prime_implicants.add(term)
                print(f"Терм {term} не участвует в склеивании")

        if new_terms == current_terms or not new_terms:
            prime_implicants.update(new_terms)
            break

        current_terms = new_terms
        iteration += 1

    print("\nТаблица простых импликант:")
    prime_implicants = sorted(list(prime_implicants))
    original_terms = sorted(terms)

    print("Импликанты |", end=" ")
    for term in original_terms:
        print(f"{term}", end="  ")
    print("\n" + "-" * (13 + 4 * len(original_terms)))

    for prime in prime_implicants:
        print(f"{prime:10} |", end=" ")
        for term in original_terms:
            matches = True
            for i in range(len(term)):
                if prime[i] != '-' and prime[i] != term[i]:
                    matches = False
                    break
            print(" × " if matches else "   ", end=" ")
        print()

    expressions = []
    for term in prime_implicants:
        expr = []
        for i, bit in enumerate(term):
            if bit == '1':
                expr.append(f"{['a', 'b', 'c'][i]}")
            elif bit == '0':
                expr.append(f"!{['a', 'b', 'c'][i]}")

        if expr:
            expressions.append('(' + '&'.join(expr) + ')')

    final_expression = ' | '.join(expressions)

    print("\nРезультат минимизации:")
    print("Простые импликанты:", prime_implicants)
    print("Минимизированная форма:", final_expression)
    return prime_implicants


def minimize_cnf_calculation_table(terms, vars_count):
    print("\nМинимизация СКНФ расчетно-табличным методом:")
    print("Исходные термы:", terms)

    iteration = 1
    current_terms = set(terms)
    prime_implicants = set()

    while True:
        print(f"\nШаг склеивания {iteration}:")
        new_terms = set()
        used_terms = set()

        terms_list = list(current_terms)
        for i in range(len(terms_list)):
            for j in range(i + 1, len(terms_list)):
                term1 = terms_list[i]
                term2 = terms_list[j]

                diff_pos = -1
                diff_count = 0
                for pos in range(len(term1)):
                    if term1[pos] != term2[pos]:
                        diff_count += 1
                        diff_pos = pos
                        if diff_count > 1:
                            break

                if diff_count == 1:
                    new_term = list(term1)
                    new_term[diff_pos] = '-'
                    new_term = ''.join(new_term)
                    new_terms.add(new_term)
                    used_terms.add(term1)
                    used_terms.add(term2)
                    print(f"Склеиваем {term1} и {term2} → {new_term}")

        for term in current_terms:
            if term not in used_terms:
                prime_implicants.add(term)
                print(f"Терм {term} не участвует в склеивании")

        if new_terms == current_terms or not new_terms:
            prime_implicants.update(new_terms)
            break

        current_terms = new_terms
        iteration += 1

    print("\nТаблица простых импликант:")
    prime_implicants = sorted(list(prime_implicants))
    original_terms = sorted(terms)

    print("Импликанты |", end=" ")
    for term in original_terms:
        print(f"{term}", end="  ")
    print("\n" + "-" * (13 + 4 * len(original_terms)))

    for prime in prime_implicants:
        print(f"{prime:10} |", end=" ")
        for term in original_terms:
            matches = True
            for i in range(len(term)):
                if prime[i] != '-' and prime[i] != term[i]:
                    matches = False
                    break
            print(" × " if matches else "   ", end=" ")
        print()

    expressions = []
    for term in prime_implicants:
        expr = []
        for i, bit in enumerate(term):
            if bit == '0':
                expr.append(f"!{['a', 'b', 'c'][i]}")
            elif bit == '1':
                expr.append(f"{['a', 'b', 'c'][i]}")

        if expr:
            expressions.append('(' + '|'.join(expr) + ')')

    final_expression = ' & '.join(expressions)

    print("\nРезультат минимизации:")
    print("Простые импликанты:", prime_implicants)
    print("Минимизированная форма:", final_expression)
    return prime_implicants


def minimize_dnf_karnaugh(truth_table, vars):
    print("\nМинимизация СДНФ методом карт Карно:")

    n_vars = len(vars)
    if n_vars == 2:
        karnaugh_map = [
            [truth_table[0], truth_table[1]],
            [truth_table[2], truth_table[3]]
        ]

        print("\nКарта Карно:")
        print("   b     0    1")
        print("a")
        print("0     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[0]))
        print("1     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[1]))

    else:
        karnaugh_map = [
            [truth_table[0], truth_table[1], truth_table[3], truth_table[2]],
            [truth_table[4], truth_table[5], truth_table[7], truth_table[6]]
        ]

        print("\nКарта Карно:")
        print("   bc    00   01   11   10")
        print("a")
        print("0     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[0]))
        print("1     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[1]))

    groups = []

    if n_vars == 2:
        if karnaugh_map[1][0] == 1 and karnaugh_map[1][1] == 1:
            groups.append("a")
        if karnaugh_map[1][0] == 1 and karnaugh_map[0][0] == 1:
            groups.append("!b")
        if karnaugh_map[1][1] == 1 and karnaugh_map[0][1] == 1:
            groups.append("b")
    else:
        if karnaugh_map[1][0] == 1 and karnaugh_map[1][1] == 1 and karnaugh_map[1][2] == 1 and karnaugh_map[1][3] == 1:
            groups.append("a")
        if karnaugh_map[0][0] == 1 and karnaugh_map[0][1] == 1 and karnaugh_map[0][2] == 1 and karnaugh_map[0][3] == 1:
            groups.append("!a")
        if karnaugh_map[0][0] == 1 and karnaugh_map[1][0] == 1 and karnaugh_map[0][3] == 1 and karnaugh_map[1][3] == 1:
            groups.append("!b")
        if karnaugh_map[0][1] == 1 and karnaugh_map[1][1] == 1 and karnaugh_map[0][2] == 1 and karnaugh_map[1][2] == 1:
            groups.append("b")
        if karnaugh_map[0][0] == 1 and karnaugh_map[0][1] == 1 and karnaugh_map[1][0] == 1 and karnaugh_map[1][1] == 1:
            groups.append("!c")
        if karnaugh_map[0][2] == 1 and karnaugh_map[0][3] == 1 and karnaugh_map[1][2] == 1 and karnaugh_map[1][3] == 1:
            groups.append("c")

    groups = list(set(groups))

    print("\nНайденные группы:", groups)
    if groups:
        minimal_form = " | ".join(f"({g})" for g in groups)
    else:
        minimal_form = "Нет групп единиц"
    print("Минимизированная форма:", minimal_form)


def minimize_cnf_karnaugh(truth_table, vars):
    print("\nМинимизация СКНФ методом карт Карно:")

    n_vars = len(vars)
    inv_table = [1 - int(x) for x in truth_table]

    if n_vars == 2:
        karnaugh_map = [
            [inv_table[0], inv_table[1]],
            [inv_table[2], inv_table[3]]
        ]

        print("\nКарта Карно (для нулей):")
        print("   b     0    1")
        print("a")
        print("0     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[0]))
        print("1     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[1]))

    else:
        karnaugh_map = [
            [inv_table[0], inv_table[1], inv_table[3], inv_table[2]],
            [inv_table[4], inv_table[5], inv_table[7], inv_table[6]]
        ]

        print("\nКарта Карно (для нулей):")
        print("   bc    00   01   11   10")
        print("a")
        print("0     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[0]))
        print("1     ", end="")
        print("   ".join(str(x) for x in karnaugh_map[1]))

    groups = []

    if n_vars == 2:
        if karnaugh_map[0][0] == 1 and karnaugh_map[0][1] == 1:
            groups.append("!a")
        if karnaugh_map[0][0] == 1 and karnaugh_map[1][0] == 1:
            groups.append("!b")
        if karnaugh_map[0][1] == 1 and karnaugh_map[1][1] == 1:
            groups.append("b")
    else:
        if karnaugh_map[0][0] == 1 and karnaugh_map[0][1] == 1 and karnaugh_map[0][2] == 1 and karnaugh_map[0][3] == 1:
            groups.append("!a")
        if karnaugh_map[1][0] == 1 and karnaugh_map[1][1] == 1 and karnaugh_map[1][2] == 1 and karnaugh_map[1][3] == 1:
            groups.append("a")
        if karnaugh_map[0][0] == 1 and karnaugh_map[1][0] == 1 and karnaugh_map[0][3] == 1 and karnaugh_map[1][3] == 1:
            groups.append("!b")
        if karnaugh_map[0][1] == 1 and karnaugh_map[1][1] == 1 and karnaugh_map[0][2] == 1 and karnaugh_map[1][2] == 1:
            groups.append("b")
        if karnaugh_map[0][0] == 1 and karnaugh_map[0][1] == 1 and karnaugh_map[1][0] == 1 and karnaugh_map[1][1] == 1:
            groups.append("!c")
        if karnaugh_map[0][2] == 1 and karnaugh_map[0][3] == 1 and karnaugh_map[1][2] == 1 and karnaugh_map[1][3] == 1:
            groups.append("c")

    groups = list(set(groups))

    print("\nНайденные группы:", groups)
    if groups:
        minimal_form = " & ".join(f"({g})" for g in groups)
    else:
        minimal_form = "Нет групп нулей"
    print("Минимизированная форма:", minimal_form)


if __name__ == '__main__':
    expr = str(input("Введите логическую функцию:"))
    vars, rpn = process_expression(expr)
    print(f"\nВыражение: {expr}")
    print("Переменные:", vars)
    print("RPN:", rpn),
    table_info = table_create(expr, rpn, vars)
    print(f"Индексная форма: {table_info['index']}")
    print(f"Числовая форма СДНФ: {table_info['pdnf']}")
    print(f"Числовая форма СКНФ: {table_info['pcnf']}")
    print(f"Совершенная дизъюнктивная нормальная форма (СДНФ): {table_info['pdnf_exp_list']}")
    print(f"Совершенная конъюнктивная нормальная форма (СKНФ): {table_info['pcnf_exp_list']}")
    print("\nРасчетный метод минимизации:")
    terms_dnf = get_binary_terms(table_info['pdnf'], len(vars))
    terms_cnf = get_binary_terms(table_info['pcnf'], len(vars))

    print(f"Термы перед минимизацией СДНФ: {terms_dnf}")
    print(f"Термы перед минимизацией СКНФ: {terms_cnf}")
    min_terms_dnf = minimize_dnf_calculation(terms_dnf, len(vars))
    min_terms_cnf = minimize_cnf_calculation(terms_cnf, len(vars))


    terms_dnf = get_binary_terms(table_info['pdnf'], len(vars))
    terms_cnf = get_binary_terms(table_info['pcnf'], len(vars))
    #
    # min_terms_dnf_table = minimize_dnf_calculation_table(terms_dnf, len(vars))
    # min_terms_cnf_table = minimize_cnf_calculation_table(terms_cnf, len(vars))
    #
    # minimize_dnf_karnaugh(table_info['index'], vars)
    # minimize_cnf_karnaugh(table_info['index'], vars)