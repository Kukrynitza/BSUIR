#include <gtest/gtest.h>
#include "GymnasticsTest.h"
#include "JoggingTest.h"
#include "WeightliftingTest.h"
#include "UserTest.h"
using namespace USER;
using namespace std;
int main(int argc, char** argv) {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
//OpenCppCoverage --sources ppois-laba-3 -- .\x64\Debug\ppois-laba-3.exe