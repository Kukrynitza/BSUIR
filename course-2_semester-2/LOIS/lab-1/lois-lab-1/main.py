 # Вариант: F14
 # Лабораторная работа №1 по дисциплине Логические Основы Интеллектуальных Систем
 # Выполнена студентом группы 321701: Политыко Ильей Андреевичем
 #
 # 01.05.2025
 #
 # Задание:
 #  Проверить является ли формула КНФ
 #
 # Использованные источники:
 # Справочная система по дисциплине ЛОИС
 # Логические основы интеллектуальных систем. Практикум


from node import *

BINARY_OPS = ["\\/", "/\\", "->", "~"]

def is_atomic(s: str) -> bool:
    return len(s) == 1 and s.isupper()

def is_const(s: str) -> bool:
    return s in ["0", "1"]

def is_unary(s: str) -> bool:
    return s.startswith("(!") and s.endswith(")") and is_formula(s[2:-1])

def is_binary(s: str) -> bool:
    if not (s.startswith("(") and s.endswith(")")):
        return False
    inner = s[1:-1]
    depth = 0
    for i in range(len(inner)):
        if inner[i] == '(':
            depth += 1
        elif inner[i] == ')':
            depth -= 1
        elif depth == 0:
            for op in BINARY_OPS:
                if inner[i:i+len(op)] == op:
                    left = inner[:i]
                    right = inner[i+len(op):]
                    return is_formula(left) and is_formula(right)
    return False

def is_formula(s: str) -> bool:
    s = s.strip()
    return is_const(s) or is_atomic(s) or is_unary(s) or is_binary(s)

def is_literal(s: str) -> bool:
    return (len(s) == 1 and s.isupper()) or (s.startswith("(!") and s.endswith(")") and len(s) == 4 and s[2].isupper())

# --- Новый блок: Упрощение вложенных выражений ---
def flatten_parentheses(expr: str) -> str:
    if expr.startswith('(') and expr.endswith(')'):
        inner = expr[1:-1]
    else:
        inner = expr
    inner_no_parens = ''
    for ch in inner:
        if ch not in '()':
            inner_no_parens += ch
    result = ''
    i = 0
    while i < len(inner_no_parens):
        if i + 1 < len(inner_no_parens) and inner_no_parens[i] == '/' and inner_no_parens[i+1] == '\\':
            result += ')/\\('
            i += 2
        else:
            result += inner_no_parens[i]
            i += 1

    return f'({result})'


 # --- Проверка КНФ ---

def no_implication_or_negation(s: str) -> bool:
    if '->' in s or '~' in s:
        return True
    return False

def is_valid_clause(clause: str):
    i = 0
    expect_literal = True
    literals = set()

    while i < len(clause):
        if clause[i].isspace():
            i += 1
            continue

        if clause[i:i+2] == "\\/":
            if expect_literal:
                return False, None
            expect_literal = True
            i += 2
        else:
            token = ""
            if clause[i] == '!':
                token += clause[i]
                i += 1
                if i >= len(clause) or not clause[i].isupper():
                    return False, None
                token += clause[i]
                i += 1
            elif clause[i].isalpha() and clause[i].isupper():
                token += clause[i]
                i += 1
                if i < len(clause) and clause[i].isalpha():
                    return False, None
            else:
                return False, None

            if token in literals:
                return False, None
            negated = token[1] if token.startswith('!') else '!' + token
            if negated in literals:
                return False, None

            literals.add(token)
            expect_literal = False

    return not expect_literal, frozenset(literals)

def is_cnf(formula: str) -> bool:
    if no_implication_or_negation(formula):
        return False
    try:
        tree = parse_formula_to_tree(formula)
    except Exception:
        return False

    if not is_strict_cnf_tree(tree):
        return False
    formula = flatten_parentheses(formula)
    # print(formula)
    i = 0
    clause_sets = set()
    expect_clause = True

    while i < len(formula):
        if formula[i].isspace():
            i += 1
            continue

        if formula[i] == '(':
            if not expect_clause:
                return False
            i += 1
            clause = ''
            paren_count = 1

            while i < len(formula) and paren_count > 0:
                if formula[i] == '(':
                    paren_count += 1
                elif formula[i] == ')':
                    paren_count -= 1

                if paren_count > 0:
                    clause += formula[i]
                i += 1

            valid, literal_set = is_valid_clause(clause)
            if not valid or literal_set in clause_sets:
                return False
            clause_sets.add(literal_set)
            expect_clause = False

        elif formula[i:i+2] == "/\\":
            if expect_clause:
                return False
            i += 2
            expect_clause = True
        else:
            return False

    return bool(clause_sets) and not expect_clause

def read_formula_from_file(filename: str) -> str:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return "".join(line.strip() for line in file)
    except FileNotFoundError:
        print("Не удалось открыть файл.")
        return ""

def user_test():
    test_cases = [
        ("((A\\/B)/\\(C\\/(!D))", True),
        ("((A\\/(!B))/\\(C\\/D\\/(!E))/\\(V\\/(!Z))/\\(A\\/S\\/(!V)))", False),
        ("(Z\\/(!Z)", False),
        ("A\\/B", False),
        ("(((A\\/B)/\\(C))", False),
        ("((A\\/B)\\/A)", False),
        ("((A\\/B)/\\(C\\/D))", True),
        ("((A\\/(!B))/\\((C\\/D)\\/(!E)))", True),
        ("(/\\(A\\/B)", False),
        ("((A\\/B)/\\", False),
        ("(A\\/1)", False),
        ("((A\\/!b)/\\(B\\/!a)", False),
        ("(((A\\/(!B))/\\(C\\/(!B)))/\\((!A)\\/C))", True),
        ("(((X\\/Y)\\/Z)/\\(((!X)\\/(!Y))\\/(!Z)))", True),
        ("(A\\/(!A))", False),
        ("()", False),
        ("(AB)", False),
        ("((A))", False),
    ]

    correct = 0
    for i, (formula, expected) in enumerate(test_cases, start=1):
        print(f"\nФормула #{i}: {formula}")
        while True:
            answer = input("Это КНФ? (1 - да, 0 - нет): ").strip()
            if answer not in ("0", "1"):
                print("Некорректный ввод. Попробуйте ещё раз.")
                continue
            user_answer = (answer == "1")
            break
        if user_answer == expected:
            print("Правильно!")
            correct += 1
        else:
            print(f"Неправильно. Правильный ответ: {'КНФ' if expected else 'не КНФ'}")
    print(f"\nВы ответили правильно на {correct} из {len(test_cases)} вопросов.")

def main():
    i = True
    while i:
        print("\nМеню:")
        print("1 - Ввод формулы с консоли")
        print("2 - Чтение формулы из файла")
        print("3 - Пройти тест на знание КНФ")
        print("4 - Автор")
        print("0 - Выход")
        # choice = "1"
        choice = input("Ваш выбор: ").strip()
        if choice == "0":
            print("Выход из программы.")
            i = False
        elif choice == "1":
            input_formula = input("Введите формулу: ").strip()
        elif choice == "2":
            filename = input("Введите имя файла: ").strip()
            input_formula = read_formula_from_file(filename)
        elif choice == "3":
            user_test()
            continue
        elif choice == "4":
            print("Политыко Илья Андреевич")
            continue
        else:
            print("Неверный выбор.")
            continue

        if not input_formula:
            print("Формула пуста.")
            continue
        input_formula = input_formula.strip()
        if is_formula(input_formula):
            print("Формула валидна")
            if is_cnf(input_formula):
                print("Формула является КНФ.")
            else:
                print("Формула не является КНФ.")
        else:
            print("Формула не валидна")

if __name__ == "__main__":
    main()

 # Введите формулу: (A->B)
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: A
 # Формула валидна.
 # Формула является СДНФ.

 # Введите формулу: (!A)
 # Формула валидна.
 # Формула является СДНФ.

 # Введите формулу: 0
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: 1
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (!0)
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (!)
 # Формула невалидна: Пустая формула
 # Введите формулу: (!1)
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (A\/(!A))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (A\/A)
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: ((A\/B)/\(A\/B))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: ((A\/B)/\(B\/A))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: ((((0\/1)\/1)/\(((1\/1)\/1))\/((0/\0)/\0))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (!(!F))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (!R)
 # Формула валидна.
 # Формула является СДНФ.

 # Введите формулу: ((1~Q2)->C)
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (((A\/B)\/C)/\((!0)\/((!A)\/((!B)\/C))))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (((((Q\/R)\/E)/\(((!E)\/(!Q))/\R))\/((R\/E)/\(!Q)))\/((Q\/R)\/E))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (((((Q\/R)\/E)/\(((!E)\/(!Q))/\R))\/((R\/E)/\(!Q)))\/((E\/Q)\/R))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (C/\O)
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: ((((!P)\/R)/\((Q\/R))\/((P\/Q)\/R))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: ((((A123\/B)\/C)/\(((!B)\/(!C))/\A123))\/(((!A123)\/B)/\(!C)))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (((A\/B)\/C)/\(!0\/((!A)\/((!B)\/C))))
 # Формула невалидна: Некорректные операнды для операции: !0\/((!A)\/((!B)\/C))
 # Введите формулу: (((A\/B)\/C)/\((!0)\/((!A)\/((!B)\/C))))
 # Формула валидна.
 # Формула не является СДНФ.

 # Введите формулу: (/\)/\(/\/)
 # Формула невалидна: Некорректные операнды для операции: /\/

 # Введите формулу: ((/\)/\(!))
 # Формула невалидна: Пустая формула

 # Введите формулу: ((((!P)\/R)->/\(Q\/R))->((P\/Q)->R))
 # Формула невалидна: <атомарная формула>|<константа>  не могут быть в скобках без унарной операции: ((!P)\/R)

 # Введите формулу: ((((!P)R)/\(Q\/R))/\((P\/Q)/\R))
 # Формула невалидна: <атомарная формула>|<константа>  не могут быть в скобках без унарной операции: ((!P)R)

 # Введите формулу: ((((!P)/\R)->\/(Q\/R))->((P\/Q)->R))
 # Формула невалидна: Некорректные операнды для операции: ((!P)/\R)->\/(Q\/R)

 # Введите формулу: (a/\b)
 # Формула невалидна: Некорректные операнды для операции: a/\b

 # Введите формулу: (P)
 # Формула невалидна: <атомарная формула>|<константа>  не могут быть в скобках без унарной операции: (P)

 # Введите формулу: ((Q2))
 # Формула невалидна: <атомарная формула>|<константа>  не могут быть в скобках без унарной операции: ((Q2))

 # Введите формулу: v
 # Формула невалидна: Некорректная структура формулы: v

 # Введите формулу: ((!Q))
 # Формула невалидна: <атомарная формула>|<константа>  не могут быть в скобках без унарной операции: ((!Q))

 # Введите формулу: 2
 # Формула невалидна: Некорректная структура формулы: 2

 # Введите формулу: R3~
 # Формула невалидна: Некорректные операнды для операции: R3~

 # Введите формулу: ~Y6
 # Формула невалидна: Некорректные операнды для операции: ~Y6
