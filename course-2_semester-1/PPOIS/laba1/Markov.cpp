#include "Markov.h"

int main() {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    Recording in;
    in.RecordText();
    in.RecordChanges();
    Deduce out(in.SetText());
    out.ApplicationOfMarkovAlgorithms(in.SetChanges());
    return 0;
}
