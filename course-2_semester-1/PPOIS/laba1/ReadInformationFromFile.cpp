#include "ReadInformationFromFile.h";

void Recording::getRecord(string rec) {
    if (rec.empty()) {
        cout << "Введите ссылку: ";
        getline(cin, this->rec);
        return;
    }
    this->rec = rec;
}
void Recording::getChanges(list<pair<string, string>> changes) {
    this->changes = changes;
}

list<pair<string, string>> Recording::setChanges() {
    return this->changes;
}

void Recording::getText(string text) {
    this->text = text;
}

string Recording::setText() {
    return this->text;
}
string Recording::setRecord() {
    return this->rec;
}

bool Recording::recordingInformationFromFile() {
    string fileInformationLine;
    ifstream record(rec);
    if (!record.is_open()) {
        cout << "Неправильно введена ссылка на файл для вывода" << endl;
        return 0;
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
                changes.push_back(make_pair(fileInformationLine.substr(discoveryOfWhatNeedsToBeChanged + 1, closingOfWhatNeedsToBeChanged - discoveryOfWhatNeedsToBeChanged - 1), fileInformationLine.substr(openingWhatNeedsToBeChanged + 1, closingWhatNeedsToBeChanged - openingWhatNeedsToBeChanged - 1)));
                continue;
            }
        }
        if (!text.empty()) {
            text += '\n';
        }
        text += fileInformationLine;
    }
    record.close();
    return 1;
}