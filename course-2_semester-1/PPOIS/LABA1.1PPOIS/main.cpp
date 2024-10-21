#include "Menu.h"
#include "ReadInformationFromFile.h"
#include "Markov.h"

int main() {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    Menu in;
    in.menuChoise();
    return 0;
}
//PPOIS-laba-1.txt

//This is the first paragraph of text.
//This is the second paragraph of text, which continues over several lines.