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
#include <list>

class Menu {
private:
	Recording recordFileInformation;
	list<pair<string, string>> changes;
	Markov marcovAlgorithm;
public:
	string getChanges(string rec);
	list<pair<string, string>> setChanges();
	void consoleLogChanges();
	void consoleLogText();
	void newChange(string whatNeedsToBeChanged, string isWhatNeedsToBeReplaced);
	void deleteChange(string changWhatNeedsDelete);
	void addChangeInFile();
	bool menuChoise(string choise);
};