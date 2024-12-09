#include <iostream>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <chrono>
#include <thread>
#include <cstring>
void print_process_info() {
    pid_t pid = getpid(); 
    pid_t ppid = getppid();

    std::cout << "Процесс с ID " << pid << " и родительский процесс с ID " << ppid << std::endl;
}

void create_process_tree(int current_level, int max_level, int process_number) {
    if (current_level > max_level) {
        return;
    }

    pid_t pid = fork();

    if (pid == 0) {
        print_process_info();

        std::cout << "Процесс с ID " << getpid() << " порождает процесс с ID " << getpid() << std::endl;

        if (current_level == max_level) {
            if (process_number == 7) { 
                std::cout << "Процесс с ID " << getpid() << " выполняет команду: whoami" << std::endl;
                execlp("whoami", "whoami", nullptr);
                std::cerr << "Ошибка: не удалось выполнить команду" << std::endl;
                exit(1);
            }
        }
        int child_process_number = process_number * 10 + 1;
        create_process_tree(current_level + 1, max_level, child_process_number);

        child_process_number = process_number * 10 + 2;
        create_process_tree(current_level + 1, max_level, child_process_number);
        std::cout << "Процесс с ID " << getpid() << " и родительский процесс с ID " << getppid() << " завершает работу." << std::endl;

        exit(0); 
    } else if (pid > 0) {
        wait(nullptr); 
    } else {
        std::cerr << "Ошибка: не удалось создать процесс на уровне " << current_level << std::endl;
    }
}

int main() {
    std::cout << "Главный процесс PID: " << getpid() << std::endl;

    create_process_tree(1, 3, 1); 

    return 0;
}
