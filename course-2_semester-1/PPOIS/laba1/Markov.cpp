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
