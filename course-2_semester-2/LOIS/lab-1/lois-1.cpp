#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cctype>

bool isValidLiteral(const std::string& token) {
    if (token.empty()) return false;
    if (token[0] == '!') {
        if (token.size() != 2) return false;
        return std::isalpha(token[1]);
    }
    else {
        return token.size() == 1 && std::isalpha(token[0]);
    }
}

bool isValidClause(const std::string& clause) {
    size_t i = 0;
    std::string token;
    bool expectLiteral = true;

    while (i < clause.size()) {
        char ch = clause[i];
        if (std::isspace(ch)) {
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
                if (i >= clause.size() || !std::isalpha(clause[i])) return false;
                token += clause[i++];
            }
            else if (std::isalpha(ch)) {
                token += ch;
                ++i;
            }
            else {
                return false;
            }

            if (!isValidLiteral(token)) return false;
            expectLiteral = false;
        }
    }
    return !expectLiteral;
}

bool isCNF(const std::string& formula) {
    size_t i = 0;
    std::vector<std::string> clauses;
    std::string clause;

    while (i < formula.size()) {
        if (std::isspace(formula[i])) {
            ++i;
            continue;
        }

        if (formula[i] == '(') {
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
        }
        else if (formula[i] == '&') {
            ++i; // skip '&'
        }
        else {
            return false; // unexpected character
        }
    }

    return !clauses.empty();
}

std::string readFormulaFromFile(const std::string& filename) {
    std::ifstream file(filename);
    std::string formula, line;
    if (!file) {
        std::cerr << "Не удалось открыть файл.\n";
        return "";
    }
    while (std::getline(file, line)) {
        formula += line;
    }
    return formula;
}

int main() {
    system("chcp 1251");
    std::string input;
    std::cout << "Выберите источник формулы:\n1 - Ввод с консоли\n2 - Чтение из файла\n> ";
    int choice;
    std::cin >> choice;
    std::cin.ignore();

    if (choice == 1) {
        std::cout << "Введите формулу: ";
        std::getline(std::cin, input);
    }
    else if (choice == 2) {
        std::string filename;
        std::cout << "Введите имя файла: ";
        std::getline(std::cin, filename);
        input = readFormulaFromFile(filename);
    }
    else {
        std::cerr << "Неверный выбор.\n";
        return 1;
    }

    if (input.empty()) {
        std::cerr << "Формула пуста.\n";
        return 1;
    }

    if (isCNF(input)) {
        std::cout << "Формула является КНФ.\n";
    }
    else {
        std::cout << "Формула не является КНФ.\n";
    }

    return 0;
}
