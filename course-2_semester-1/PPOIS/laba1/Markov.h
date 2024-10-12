#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <math.h>
#include <iomanip>
#include <map>
#include <sstream>
#include "ReadInformationFromFile.h"
#include "Markov.h"
#include <unordered_map>


class Deduce {
private:
    string text;
    unordered_map<string, string> changes;
public:
    void getText(string text) {
        this->text = text;
    }
    void getChanges(unordered_map<string, string> changes) {
        this->changes = changes;
    }
    void applicationofmarkovalgorithms() {
        for (const auto& pair : changes) {
            size_t start = 0;
            while (true) {
                start = text.find(pair.first, start);
                if (start != string::npos) {
                    text.replace(start, pair.first.size(), pair.second);
                    cout << text << endl <<endl;
                    start += pair.second.size();
                }
                else {
                    break;
                }
            }
        }
    }
};

//C:\Users\37533\Desktop\course-2_semester-1\PPOIS\laba1\PPOIS-laba-1.txt