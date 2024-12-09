#include <iostream>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <chrono>
#include <thread>
#include <iomanip>

std::string format_time(long long milliseconds) {
    int hours = milliseconds / 3600000; 
    int minutes = (milliseconds % 3600000) / 60000;
    int seconds = (milliseconds % 60000) / 1000;
    int ms = milliseconds % 1000;

    std::ostringstream oss;
    oss << std::setfill('0') << std::setw(2) << hours << ":"
        << std::setfill('0') << std::setw(2) << minutes << ":"
        << std::setfill('0') << std::setw(2) << seconds << ":"
        << std::setfill('0') << std::setw(3) << ms;

    return oss.str();
}

void process_function(int process_number, int delay_ms, std::chrono::steady_clock::time_point start_time) {
    int iterations = 10; 

    for (int i = 0; i < iterations; ++i) {
        pid_t pid = getpid();   
        pid_t ppid = getppid();

        auto current_time = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time);
        long long milliseconds = duration.count();

        std::cout << "Процесс: " << process_number
                  << " | PID: " << pid
                  << " | PPID: " << ppid
                  << " | Время: " << format_time(milliseconds) 
                  << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
    }
}

void create_process_tree(int current_level, int max_level, int process_number, std::chrono::steady_clock::time_point start_time) {
    if (current_level > max_level) {
        return; 
    }

    pid_t pid = fork();

    if (pid == 0) {
        std::cout << "Создан дочерний процесс с PID: " << getpid()
                  << " | Родительский PID: " << getppid()
                  << " | Уровень: " << current_level
                  << " | Номер процесса: " << process_number
                  << std::endl;

        int delay_ms = process_number * 0.5;
        if (current_level < max_level) {
            int child_process_number = process_number * 10 + 1;
            create_process_tree(current_level + 1, max_level, child_process_number, start_time);

            child_process_number = process_number * 10 + 2;
            create_process_tree(current_level + 1, max_level, child_process_number, start_time);
        }

        process_function(process_number, delay_ms, start_time);
        exit(0); 
    } else if (pid > 0) {
        wait(nullptr);
    } else {
        std::cerr << "Ошибка: не удалось создать процесс на уровне " << current_level << std::endl;
    }
}

int main() {
    int max_level = 4; 

    auto start_time = std::chrono::steady_clock::now();

    std::cout << "Главный процесс PID: " << getpid() << std::endl;

    create_process_tree(1, max_level, 1, start_time);
    return 0;
}
