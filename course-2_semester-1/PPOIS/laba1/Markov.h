#pragma once
#include <iostream>
#include <string>
#include <map>

using namespace std;

class Recording {
private:
    string text;
    map<string, string> changes;
public:
    void RecordText() {
        cout << "¬ведите текст: ";
        getline(cin, text);
        cout << endl;
    }

    map<string, string> SetChanges() {
        return this->changes;
    }

    string SetText() {
        return this->text;
    }

    void RecordChanges() {
        string variable_string, replacement_string;
        while (true) {
            cout << "¬ведите строку, которую мен€ете (введите STOP, если завершаете ввод): ";
            getline(cin, variable_string);
            if (variable_string == "STOP") {
                break;
            }
            cout << "¬ведите строку, на которую мен€ете: ";
            getline(cin, replacement_string);
            this->changes.insert(make_pair(variable_string, replacement_string));
        }
    }
};

class Deduce {
private:
    string text;
public:
    Deduce(string text) {
        this->text = text;
    }

    void ApplicationOfMarkovAlgorithms(map<string, string> changes) {
        for (const auto& pair : changes) {
            size_t start = 0;
            while (true) {
                start = text.find(pair.first, start);
                if (start != string::npos) {
                    text.replace(start, pair.first.size(), pair.second);
                    cout << text << endl;
                    start += pair.second.size();
                }
                else {
                    break;
                }
            }
        }
    }
};