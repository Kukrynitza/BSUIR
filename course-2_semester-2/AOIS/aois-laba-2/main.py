import math
import string


def binary_to_decimal(binary_str: str) -> int:
    decimal_number = 0
    power = len(binary_str) - 1

    for digit in binary_str:
        decimal_number += int(digit) * (2 ** power)
        power -= 1

    return decimal_number


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
            el:int = make_operation(vars[-1], vars[-2], rpn[element])
            vars.pop()
            vars.pop()
            vars.append(el)
    return vars[0]


def table_create(exp: str, rpn: list, vars: list):
    vars_in_degree: int = 2 ** len(vars)
    vars_string: str = ''
    for i in vars:
        vars_string += i + ' '
    vars_string += '' + exp
    print(vars_string)
    index_form: list = []
    pdnf_exp_list: str = ''
    pcnf_exp_list: str = ''
    pdnf_list: list = []
    pcnf_list: list = []
    for i in range(vars_in_degree):
        bool_vars = to_bin(i, len(vars))
        str_numbers = [str(n) for n in bool_vars]
        bool_rpn: list = rpn.copy()
        for f in range(len(vars)):
            indices = [index for index, val in enumerate(bool_rpn) if val == vars[f]]
            for index in indices:
                if '!' in vars[f]:
                    bool_rpn[index] = 1 - bool_vars[f]
                else:
                    bool_rpn[index] = bool_vars[f]
        check_info = rpn_check(bool_rpn)
        index_form.append(str(check_info))
        bool_vars_string = ' '.join(str_numbers) + '  ' + str(check_info)
        result_exp = ''
        if check_info == 1:
            for f in range(len(vars)):
                if bool_vars[f] == 1:
                    result_exp += vars[f].replace('!', '')
                else:
                    result_exp += '!' + vars[f].replace('!', '')
                if check_info == 1 and f + 1 != len(vars):
                    result_exp += '&'
            pdnf_list.append(str(i))
            pdnf_exp_list += '(' + result_exp + ')|'
        else:
            for f in range(len(vars)):
                if bool_vars[f] == 1:
                    result_exp += '!' + vars[f].replace('!', '')
                else:
                    result_exp += vars[f].replace('!', '')
                if check_info == 0 and f + 1 != len(vars):
                    result_exp += '|'
            pcnf_list.append(str(i))
            pcnf_exp_list += '(' + result_exp + ')&'
        print(bool_vars_string)
    if len(pdnf_exp_list) != 0:
        pdnf_exp_list = pdnf_exp_list[:-1]
    if len(pcnf_exp_list) != 0:
        pcnf_exp_list = pcnf_exp_list[:-1]
    return {'index': ''.join(index_form), 'pdnf': '(' + ', '.join(pdnf_list) + ')&', 'pcnf': '(' + ', '.join(pcnf_list) + ')|', 'pdnf_exp_list': pdnf_exp_list,
            'pcnf_exp_list': pcnf_exp_list}


if __name__ == '__main__':
    expr = str(input("Введите логическую функцию:"))
    vars, rpn = process_expression(expr)
    print(f"\nВыражение: {expr}")
    print("Переменные:", vars)
    print("RPN:", rpn),
    table_info = table_create(expr, rpn, vars)
    decimal = binary_to_decimal(table_info['index'])
    print(f"{decimal} - Индексная форма: {table_info['index']}")
    print(f"Числовая форма СДНФ: {table_info['pdnf']}")
    print(f"Числовая форма СКНФ: {table_info['pcnf']}")
    print(f"Совершенная дизъюнктивная нормальная форма (СДНФ): {table_info['pdnf_exp_list']}")
    print(f"Совершенная конъюнктивная нормальная форма (СKНФ): {table_info['pcnf_exp_list']}")
