#include <gtest/gtest.h>
#include "GraphTest.h"

int main(int argc, char** argv) {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

//OpenCppCoverage --sources LABA1.1PPOIS -- .\x64\Debug\LABA1.1PPOIS.exe