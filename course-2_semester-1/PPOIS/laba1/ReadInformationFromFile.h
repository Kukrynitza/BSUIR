#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <math.h>
#include <iomanip>
#include <map>
#include <unordered_map>
#include <sstream>
using namespace std;

class Recording {
private:
    string text, rec;
    unordered_map<string, string> changes;
public:
    void getRecord() {
        cout << "Введите ссылку: ";
        getline(cin, this->rec);
    }
    void getChanges(unordered_map<string, string> changes) {
        this->changes = changes;
    }

    unordered_map<string, string> setChanges() {
        return this->changes;
    }

    string setText() {
        return this->text;
    }
    string setRecord() {
        return this->rec;
    }

    void recordingInformationFromFile() {
        string fileInformationLine;
        ifstream record(rec);
        if (!record.is_open()) {
            cout << "Неправильно введена ссылка на файл для вывода" << endl;
        }
        while (getline(record, fileInformationLine)) {
            if (fileInformationLine.empty()) {
                continue;
            }
            if (fileInformationLine.find("CHNG:") != string::npos) {
                size_t discoveryOfWhatNeedsToBeChanged = fileInformationLine.find('<');
                size_t closingOfWhatNeedsToBeChanged = fileInformationLine.find('>', discoveryOfWhatNeedsToBeChanged + 1);
                size_t changeArrow = fileInformationLine.find(">>", closingOfWhatNeedsToBeChanged + 1);
                size_t openingWhatNeedsToBeChanged = fileInformationLine.find('<', changeArrow + 2);
                size_t closingWhatNeedsToBeChanged = fileInformationLine.find('>', openingWhatNeedsToBeChanged + 1);

                if (discoveryOfWhatNeedsToBeChanged != string::npos && closingOfWhatNeedsToBeChanged != string::npos &&
                    changeArrow != string::npos && openingWhatNeedsToBeChanged != string::npos && closingWhatNeedsToBeChanged != string::npos) {
                    changes.insert(make_pair(fileInformationLine.substr(discoveryOfWhatNeedsToBeChanged + 1, closingOfWhatNeedsToBeChanged - discoveryOfWhatNeedsToBeChanged - 1), fileInformationLine.substr(openingWhatNeedsToBeChanged + 1, closingWhatNeedsToBeChanged - openingWhatNeedsToBeChanged - 1)));
                    continue;
                }
            }
            if (!text.empty()) {
                text += '\n';
            }
            text += fileInformationLine;
        }
        record.close();
    }
};