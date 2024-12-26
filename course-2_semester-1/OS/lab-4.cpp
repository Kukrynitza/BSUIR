#include <iostream>
#include <vector>
#include <map>
#include <stdexcept> #include <cstring>
class MemManager { private:
    size_t totalMem;     size_t usedMem;
    void* baseMem; // Базовый блок памяти
    std::map<void*, size_t> allocatedBlocks; // Адрес блока -> размер блока     std::vector<std::pair<void*, size_t>> freeBlocks; // Адрес блока -> размер блока
public:
    explicit MemManager(size_t memSize) : totalMem(memSize), usedMem(0) {         baseMem = malloc(memSize); // Выделение единого блока памяти         if (!baseMem) {
            throw std::runtime_error("Ошибка инициализации памяти");
        }
        freeBlocks.emplace_back(baseMem, memSize);
    }
    ~MemManager() {
        free(baseMem); // Освобождаем только базовый блок
    }
    // Выделение блока памяти     void* allocate(size_t size) {
        for (auto it = freeBlocks.begin(); it != freeBlocks.end(); ++it) {             if (it->second >= size) {                 void* block = it->first;                 size_t remaining = it->second - size;
                // Удаляем текущий свободный блок                 freeBlocks.erase(it);
                // Если осталась свободная память, добавляем её обратно                 if (remaining > 0) {
                    void* remainingBlock = static_cast<char*>(block) + size;                     freeBlocks.emplace_back(remainingBlock, remaining);
                }
                allocatedBlocks[block] = size;                 usedMem += size;
                return block;
            }
        }
        throw std::runtime_error("Недостаточно памяти для выделения блока");
    }
    // Освобождение блока памяти     void deallocate(void* block) {         auto it = allocatedBlocks.find(block);
        if (it == allocatedBlocks.end()) {
            throw std::runtime_error("Блок не найден или не был выделен");
        }
        size_t size = it->second;         allocatedBlocks.erase(it);         usedMem -= size;
        freeBlocks.emplace_back(block, size);
    }
    // Запись данных в блок памяти
    void write(void* block, const void* data, size_t size) {         auto it = allocatedBlocks.find(block);
        if (it == allocatedBlocks.end()) {
            throw std::runtime_error("Блок не найден или не был выделен");
        }
        if (size > it->second) {
            throw std::runtime_error("Размер данных превышает размер блока");
        }
        memcpy(block, data, size);
    }
    // Чтение данных из блока памяти     void read(void* block, void* buffer, size_t size) {         auto it = allocatedBlocks.find(block);
        if (it == allocatedBlocks.end()) {
            throw std::runtime_error("Блок не найден или не был выделен");
        }
        if (size > it->second) {
            throw std::runtime_error("Размер данных превышает размер блока");
        }
        memcpy(buffer, block, size);
    }
    // Отображение состояния памяти
    void printStatus() const {
        std::cout << "Общая память: " << totalMem << " байт\n";         std::cout << "Используемая память: " << usedMem << " байт\n";         std::cout << "Свободные блоки: " << freeBlocks.size() << "\n";
        for (const auto& block : freeBlocks) {
            std::cout << "  Адрес: " << block.first << ", Размер: " << block.second << " байт\n";
        }
        std::cout << "Выделенные блоки: " << allocatedBlocks.size() << "\n";
        for (const auto& block : allocatedBlocks) {
            std::cout << "  Адрес: " << block.first << ", Размер: " << block.second << " байт\n";
        }     }
    // Дополнительный метод для тестов     size_t getUsedMem() const {
        return usedMem;
    }
    size_t getFreeBlocksCount() const {         return freeBlocks.size();
    }
    size_t getAllocatedBlocksCount() const {         return allocatedBlocks.size();
    } };