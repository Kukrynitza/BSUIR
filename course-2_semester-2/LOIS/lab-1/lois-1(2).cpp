// Вариант: F14
//﻿ Лабораторная работа №1 по дисциплине Логические Основы Интеллектуальных Систем
// Выполнена студентом группы 321701: Политыко Ильей Андреевичем
//
// 01.05.2025
//
// Задание:
//  Проверить является ли формула КНФ
//
// Использованные источники:
// Справочная система по дисциплине ЛОИС
// Логические основы интеллектуальных систем. Практикум

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_set>
#include <cctype>

using namespace std;

bool isAtomic(const string& str);
bool isConst(const string& str);
bool isUnary(const string& str);
bool isBinary(const string& str);
bool isFormula(const string& str);
bool isValidLiteral(const string& token);
bool isValidClause(const string& clause);
bool isCNF(string formula);
string readFormulaFromFile(const string& filename);
void userTest();

const vector<string> BINARY_OPS = { "\\/", "/\\", "->", "~" };

// Проверка, является ли строка атомарной формулой (одна заглавная буква)
bool isAtomic(const string& str) {
    return str.size() == 1 && isupper(str[0]);
}

// Проверка, является ли строка константой
bool isConst(const string& str) {
    return str == "0" || str == "1";
}

// Проверка на унарную формулу (!A, !(A\/B))
bool isUnary(const string& str) {
    if (str.size() < 4 || str.substr(0, 2) != "(!" || str.back() != ')') return false;
    return isFormula(str.substr(2, str.size() - 3));
}

// Парсинг бинарной формулы (A /\ B), рекурсивно
bool isBinary(const string& str) {
    if (str.front() != '(' || str.back() != ')') return false;

    string inner = str.substr(1, str.size() - 2);
    int depth = 0;

    for (size_t i = 0; i < inner.size(); ++i) {
        if (inner[i] == '(') depth++;
        else if (inner[i] == ')') depth--;
        else {
            for (const string& op : BINARY_OPS) {
                if (depth == 0 && inner.substr(i, op.size()) == op) {
                    string left = inner.substr(0, i);
                    string right = inner.substr(i + op.size());
                    return isFormula(left) && isFormula(right);
                }
            }
        }
    }
    return false;
}

// Основная проверка: формула ли это
bool isFormula(const string& str) {
    if (str.empty()) return false;
    if (isConst(str)) return true;
    if (isAtomic(str)) return true;
    if (isUnary(str)) return true;
    if (isBinary(str)) return true;
    return false;
}

bool isValidLiteral(const string& token) {
    if (token.empty()) return false;
    if (token[0] == '!') {
        if (token.size() != 2) return false;
        return token[1] >= 'A' && token[1] <= 'Z';
    }
    else {
        return token.size() == 1 && token[0] >= 'A' && token[0] <= 'Z';
    }
}

bool isValidClause(const string& clause) {
    size_t i = 0;
    string token;
    bool expectLiteral = true;
    unordered_set<string> literals;

    while (i < clause.size()) {
        if (isspace(clause[i])) {
            ++i;
            continue;
        }

        if (clause.substr(i, 2) == "\\/") {
            if (expectLiteral) return false;
            expectLiteral = true;
            i += 2;
        }
        else {
            token.clear();
            if (clause[i] == '!') {
                token += clause[i++];
                if (i >= clause.size() || clause[i] < 'A' || clause[i] > 'Z') return false;
                token += clause[i++];
            }
            else if (isalpha(clause[i]) && isupper(clause[i])) {
                token += clause[i++];
                if (i < clause.size() && isalpha(clause[i])) return false;
            }
            else {
                return false;
            }

            if (!isValidLiteral(token)) return false;

            if (literals.count(token)) return false;
            string negated = (token[0] == '!') ? string(1, token[1]) : ("!" + token);
            if (literals.count(negated)) return false;

            literals.insert(token);
            expectLiteral = false;
        }
    }

    return !expectLiteral;
}

bool isCNF(string formula) {
    // Удаление внешних скобок, если они оборачивают всю формулу
    while (formula.front() == '(' && formula.back() == ')') {
        int depth = 0;
        bool valid = true;
        for (size_t i = 0; i < formula.size(); ++i) {
            if (formula[i] == '(') depth++;
            else if (formula[i] == ')') depth--;
            if (depth == 0 && i != formula.size() - 1) {
                valid = false;
                break;
            }
        }
        if (valid) {
            formula = formula.substr(1, formula.size() - 2);
        }
        else {
            break;
        }
    }

    // далее — как раньше
    size_t i = 0;
    vector<string> clauses;
    string clause;
    bool expectClause = true;

    while (i < formula.size()) {
        if (isspace(formula[i])) {
            ++i;
            continue;
        }

        if (formula[i] == '(') {
            if (!expectClause) return false;
            ++i;
            clause.clear();
            int parenCount = 1;

            while (i < formula.size() && parenCount > 0) {
                if (formula[i] == '(') parenCount++;
                else if (formula[i] == ')') parenCount--;

                if (parenCount > 0) clause += formula[i];
                ++i;
            }

            if (parenCount != 0 || !isValidClause(clause)) return false;
            clauses.push_back(clause);
            expectClause = false;
        }
        else if (formula.substr(i, 2) == "/\\") {
            if (expectClause) return false;
            i += 2;
            expectClause = true;
        }
        else {
            return false;
        }
    }

    return !clauses.empty() && !expectClause;
}

string readFormulaFromFile(const string& filename) {
    ifstream file(filename);
    string formula, line;
    if (!file) {
        cerr << "Не удалось открыть файл.\n";
        return "";
    }
    while (getline(file, line)) {
        formula += line;
    }
    return formula;
}

void userTest() {
    vector<pair<string, bool>> testCases = {
        {"(A\\/B)/\\(C\\/!D)", true},
        {"(A\\/!B)/\\(C\\/D\\/!E)/\\(V\\/!Z)/\\(A\\/S\\/!V)", false},
        {"(Z\\/!Z)", false},
        {"A\\/B", false},
        {"((A\\/B)/\\(C))", false},
        {"(A\\/B\\/A)", false},
        {"(A\\/B)/\\(C\\/D)", true},
        {"(A\\/!B)/\\(C\\/D\\/!E)", true},
        {"/\\(A\\/B)", false},
        {"(A\\/B)/\\", false},
        {"(A\\/1)", false},
        {"(A\\/!b)/\\(B\\/!a)", false},
        {"(A\\/!B)/\\(C\\/!B)/\\(!A\\/C)", true},
        {"(X\\/Y\\/Z)/\\(!X\\/!Y\\/!Z)", true},
        {"(A\\/!A)", false},
        {"()", false},
        {"(AB)", false},
        {"((A))", false}
    };

    int correct = 0;
    for (size_t i = 0; i < testCases.size(); ++i) {
        cout << "\nФормула #" << i + 1 << ": " << testCases[i].first << "\n";
        cout << "Это КНФ? (1 - да, 0 - нет): ";
        string answer;
        getline(cin, answer);
        if (answer != "0" && answer != "1") {
            cout << "Некорректный ввод. Пропускаем.\n";
            continue;
        }

        bool userAnswer = (answer == "1");
        if (userAnswer == testCases[i].second) {
            cout << "Правильно!\n";
            ++correct;
        }
        else {
            cout << "Неправильно. ";
            cout << "Правильный ответ: " << (testCases[i].second ? "КНФ" : "не КНФ") << "\n";
        }
    }

    cout << "\nВы ответили правильно на " << correct << " из " << testCases.size() << " вопросов.\n";
}

int main() {
    system("chcp 1251");
    while (true) {
        string input;
        cout << "\nМеню:\n";
        cout << "1 - Ввод формулы с консоли\n";
        cout << "2 - Чтение формулы из файла\n";
        cout << "3 - Пройти тест на знание КНФ\n";
        cout << "4 - Автор\n";
        cout << "0 - Выход\n";
        cout << "Ваш выбор: ";
        int choice;
        cin >> choice;
        cin.ignore();

        if (choice == 0) {
            cout << "Выход из программы.\n";
            break;
        }
        else if (choice == 1) {
            cout << "Введите формулу: ";
            getline(cin, input);
        }
        else if (choice == 2) {
            string filename;
            cout << "Введите имя файла: ";
            getline(cin, filename);
            input = readFormulaFromFile(filename);
        }
        else if (choice == 3) {
            userTest();
            continue;
        }
        else if (choice == 4) {
            cout << "Политыко Илья Андреевич\n";
            continue;
        }
        else {
            cerr << "Неверный выбор.\n";
            continue;
        }

        if (input.empty()) {
            cerr << "Формула пуста.\n";
            continue;
        }

        if (isFormula(input)) {
            cout << "Формула валидна\n";
            if (isCNF(input)) {
                cout << "Формула является КНФ.\n";
            }
            else {
                cout << "Формула не является КНФ.\n";
            }
        }
        else {
            cout << "Формула не валидна\n";
        }
    }
    return 0;
}

