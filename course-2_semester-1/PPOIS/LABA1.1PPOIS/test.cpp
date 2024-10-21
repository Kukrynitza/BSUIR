#include <gtest/gtest.h>
#include "Markov.h"
#include "ReadInformationFromFile.h"
#include "Menu.h"

TEST(MarkovTest, MarkovAlgorithmApplication) {
    Markov markov;
    string initialText = "I love google_test";
    list<pair<string, string>> changes = { {"I", "Google"}, {"v", "g"}, {"og", "g"} };
    markov.getText(initialText);  
    markov.getChanges(changes);   
    markov.applicationofmarkovalgorithms();
    EXPECT_EQ(markov.setText(), "Gogle lge gogle_test");
}

TEST(MarkovTest, MarkovSetChanges) {
    Markov markov;
    list<pair<string, string>> changes = { {"I", "Google"}, {"v", "g"}, {"og", "g"} };
    markov.getChanges(changes);
    EXPECT_EQ(markov.setChanges(), changes);
}

TEST(RecordingTest, FileRecordingFailure) {
    Recording rec;
    rec.getRecord("C:\\Users\\3733\\Desktop\\course-2_semester-1\\PPOIS\\laba1\\PPOIS-1.txt");
    EXPECT_FALSE(rec.recordingInformationFromFile());
}

TEST(RecordingTest, FileGetText) {
    Recording rec;
    rec.getText("asdx");
    EXPECT_EQ(rec.setText(), "asdx");
}

TEST(RecordingTest, FileGetChanges) {
    Recording rec;
    list<pair<string, string>> changes = { {"I", "Google"}, {"v", "g"}, {"og", "g"} };
    rec.getChanges(changes);
    EXPECT_FALSE(rec.recordingInformationFromFile());
}

TEST(RecordingTest, FileRecordingSuccess) {
    Recording rec;
    rec.getRecord("C:\\Users\\37533\\Desktop\\course-2_semester-1\\PPOIS\\laba1\\PPOIS-laba-1.txt");
    EXPECT_TRUE(rec.recordingInformationFromFile());
    EXPECT_EQ(rec.setText(), "This is the first paragraph of text.\nThis is the second paragraph of text, which continues over several lines.");
    EXPECT_EQ(rec.setChanges().size(), 7); 
}
TEST(MenuTest, AddAndDeleteChanges) {
    Menu menu;
    menu.getChanges("C:\\Users\\37533\\Desktop\\course-2_semester-1\\PPOIS\\laba1\\PPOIS-laba-1.txt");
    EXPECT_EQ(menu.setChanges().size(), 7);
    menu.newChange("sa", "de");
    EXPECT_EQ(menu.setChanges().size(), 8);

    menu.deleteChange("sa");
    EXPECT_EQ(menu.setChanges().size(), 7);
}

TEST(MenuTest, MunuChoise) {
    Menu menu;
    EXPECT_TRUE(menu.menuChoise("6"));
}

TEST(MenuTest, ConsoleOutputTest) {
    Menu menu;
    menu.getChanges("C:\\Users\\37533\\Desktop\\course-2_semester-1\\PPOIS\\laba1\\PPOIS-laba-1.txt");
    testing::internal::CaptureStdout();
    menu.consoleLogText();
    std::string output = testing::internal::GetCapturedStdout();

    EXPECT_EQ(output, "This is the first paragraph of text.\nThis is the second paragraph of text, which continues over several lines.\n\n"); 
}

TEST(MenuTest, ConsoleOutputChanges) {
    Menu menu;
    menu.getChanges("C:\\Users\\37533\\Desktop\\course-2_semester-1\\PPOIS\\laba1\\PPOIS-laba-1.txt");
    testing::internal::CaptureStdout();
    menu.consoleLogChanges();
    std::string output = testing::internal::GetCapturedStdout();
    EXPECT_EQ(output, "dfg >> f\nis >> at\nat >> v\nov >> e\ncss >> as\nas >> at\nat >> the\n\n");
}

int main(int argc, char** argv) {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}