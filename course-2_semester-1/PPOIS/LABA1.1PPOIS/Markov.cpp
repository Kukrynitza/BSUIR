#include "Markov.h"

void Markov::getText(string text) {
    this->text = text;
}
void Markov::getChanges(list<pair<string, string>> changes) {
    this->changes = changes;
}

string Markov::setText() {
    return text;
}

list<pair<string, string>> Markov::setChanges() {
    return changes;
}

void Markov::applicationofmarkovalgorithms() {
    for (const auto& pair : changes) {
        size_t start = 0;
        while (true) {
            start = text.find(pair.first, start);
            if (start != string::npos) {
                text.replace(start, pair.first.size(), pair.second);
                cout << text << endl << endl;
                start += pair.second.size();
            }
            else {
                break;
            }
        }
    }
}