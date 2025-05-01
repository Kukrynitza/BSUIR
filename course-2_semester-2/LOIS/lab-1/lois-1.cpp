#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cctype>
//Политыко Илья Андреевич
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

bool isCNF(const string& formula) {
    size_t i = 0;
    vector<string> clauses;
    string clause;

    while (i < formula.size()) {
        if (isspace(formula[i])) {
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
            ++i; 
        }
        else {
            return false; 
        }
    }

    return !clauses.empty();
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

int main() {
    system("chcp 1251");
    string input;
    cout << "Выберите источник формулы:\n1 - Ввод с консоли\n2 - Чтение из файла\n3 - Автор\n> ";
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
        cout << "Политыко Илья Андреевич";

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
