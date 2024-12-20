#include <iostream>
#include <semaphore.h>
#include <pthread.h>
#include <unistd.h>
#include <vector>
#include <cstdlib>

const int NUM_PHILOSOPHERS = 5;
sem_t forks[NUM_PHILOSOPHERS];
sem_t access_lock; // Для предотвращения deadlock

void think(int id) {
    std::cout << "Philosopher " << id << " is thinking...\n";
    sleep(rand() % 3 + 1);
}

void eat(int id) {
    std::cout << "Philosopher " << id << " is eating...\n";
    sleep(rand() % 3 + 1);
}

void* philosopher(void* arg) {
    int id = *(int*)arg;
    int left_fork = id;
    int right_fork = (id + 1) % NUM_PHILOSOPHERS;

    while (true) {
        think(id);

        // Взять вилки с защитой от взаимоблокировки
        sem_wait(&access_lock);
        sem_wait(&forks[left_fork]);
        sem_wait(&forks[right_fork]);
        sem_post(&access_lock);

        eat(id);

        // Положить вилки
        sem_post(&forks[left_fork]);
        sem_post(&forks[right_fork]);
    }

    return nullptr;
}

int main() {
    srand(time(nullptr));

    // Инициализация семафоров
    sem_init(&access_lock, 0, 1);
    for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
        sem_init(&forks[i], 0, 1);
    }

    // Создание потоков-философов
    pthread_t philosophers[NUM_PHILOSOPHERS];
    std::vector<int> ids(NUM_PHILOSOPHERS);
    for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
        ids[i] = i;
        pthread_create(&philosophers[i], nullptr, philosopher, &ids[i]);
    }

    // Ожидание завершения потоков (в данном случае бесконечно)
    for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
        pthread_join(philosophers[i], nullptr);
    }

    // Очистка ресурсов
    for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
        sem_destroy(&forks[i]);
    }
    sem_destroy(&access_lock);

    return 0;
}
