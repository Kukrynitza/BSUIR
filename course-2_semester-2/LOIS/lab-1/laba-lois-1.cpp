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

bool isValidLiteral(const string& token) {
    if (token.empty()) return false;
    if (token[0] == '!') {
        if (token.size() != 2) return false;
        return isalpha(token[1]);
    }
    else {
        return token.size() == 1 && isalpha(token[0]);
    }
}

bool isValidClause(const string& clause) {
    size_t i = 0;
    string token;
    bool expectLiteral = true;
    unordered_set<string> literals;

    while (i < clause.size()) {
        char ch = clause[i];
        if (isspace(ch)) {
            ++i;
            continue;
        }

        if (ch == '|') {
            if (expectLiteral) return false;
            expectLiteral = true;
            ++i;
        }
        else {
            token.clear();
            if (ch == '!') {
                token += ch;
                ++i;
                if (i >= clause.size() || !isalpha(clause[i])) return false;
                token += clause[i++];
            }
            else if (isalpha(ch)) {
                token += ch;
                ++i;
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

bool isCNF(const string& formula) {
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

                if (parenCount > 0) {
                    clause += formula[i];
                }
                ++i;
            }

            if (parenCount != 0 || !isValidClause(clause)) return false;
            clauses.push_back(clause);
            expectClause = false;
        }
        else if (formula[i] == '&') {
            if (expectClause) return false;
            ++i;
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
    {"(A|B)&(C|!D)", true},
    {"(A|!B)&(C|D|!E)&(V|!Z)&&(A|S|!V)", false},
    {"(Z|!Z)", false},
    {"A|B", false},
    {"((A|B)&(C))", false},
    {"(A|B|A)", false},
    {"(A|B)&(C|D)", true},
    {"(A|!B)&(C|D|!E)", true},
    {"&(A|B)", false},
    {"(A|B)&", false},
    {"(A|1)", false},
    {"(A|!b)&(B|!a)", true},
    {"(A|!B)&(C|!B)&(!A|C)", true},
    {"(X|Y|Z)&(!X|!Y|!Z)", true},
    {"(A|!A)", false},
    {"()", false},
    {"(AB)", false},
    {"((A))", false},
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
    string input;
    cout << "Выберите источник формулы:\n";
    cout << "1 - Ввод с консоли\n";
    cout << "2 - Чтение из файла\n";
    cout << "3 - Пройти тест на знание КНФ\n";
    cout << "4 - Автор\n";
    int choice;
    cin >> choice;
    cin.ignore();

    if (choice == 1) {
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
        return 1;
    }
    else if (choice == 4) {
        cout << "Политыко Илья Андреевич\n";
        return 1;
    }
    else {
        cerr << "Неверный выбор.\n";
        return 1;
    }

    if (input.empty()) {
        cerr << "Формула пуста.\n";
        return 1;
    }

    if (isCNF(input)) {
        cout << "Формула является КНФ.\n";
    }
    else {
        cout << "Формула не является КНФ.\n";
    }

    return 0;
}

