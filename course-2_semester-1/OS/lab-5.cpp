#include <iostream>
#include <string>
#include <vector>
#include <fstream>
using namespace std;

const int DISK_SIZE = 1024;  

struct File {
     string name;
    int start;         
    int size;          
};

class FileSystem {
private:
    char disk[DISK_SIZE];              
     vector<File> files;          
    int freeSpace;                      

    int findFreeSpace(int size) {
         
        int freeCount = 0;
        for (int i = 0; i < DISK_SIZE; i++) {
            if (disk[i] == '\0') {
                freeCount++;
                if (freeCount == size) {
                    return i - size + 1;  
                }
            } else {
                freeCount = 0;
            }
        }
        return -1; 
    }

public:
    FileSystem() : freeSpace(DISK_SIZE) {
         fill(disk, disk + DISK_SIZE, '\0');
    }

    void createFile(const  string& name, int size) {
        if (size > freeSpace) {
             cout << "Ошибка: недостаточно места для файла " << name << "\n";
            return;
        }

        int startIndex = findFreeSpace(size);
        if (startIndex == -1) {
             cout << "Ошибка: невозможно найти непрерывный блок для файла " << name << "\n";
            return;
        }

        
        files.push_back({name, startIndex, size});
        for (int i = startIndex; i < startIndex + size; i++) {
            disk[i] = '*';  
        }

        freeSpace -= size;
         cout << "Файл " << name << " успешно создан \n";
    }

    void deleteFile(const  string& name) {
        for (auto it = files.begin(); it != files.end(); ++it) {
            if (it->name == name) {
                 
                for (int i = it->start; i < it->start + it->size; i++) {
                    disk[i] = '\0';
                }
                freeSpace += it->size;
                files.erase(it);
                 cout << "Файл " << name << " успешно удален.\n";
                return;
            }
        }
    }

    void writeFile(const  string& name, const  string& content) {
        for (auto& file : files) {
            if (file.name == name) {
                if (content.size() > file.size) {
                     cout << "Ошибка: содержимое превышает размер файла " << name << "\n";
                    return;
                }

                 
                for (int i = 0; i < content.size(); i++) {
                    disk[file.start + i] = content[i];
                }
                 cout << "Данные успешно записаны в файл \n";
                return;
            }
        }
         cout << "Ошибка: файл " << name << " не найден.\n";
    }

    void readFile(const  string& name) {
        for (const auto& file : files) {
            if (file.name == name) {
                 cout << "Содержимое файла " << name << " : ";
                for (int i = file.start; i < file.start + file.size; i++) {
                    if (disk[i] != '\0') {
                         cout << disk[i];
                    }
                }
                 cout << "\n";
                return;
            }
        }
         cout << "Ошибка: файл " << name << " не найден.\n";
    }

    void copyFile(const  string& srcName, const  string& destName) {
    	for (const auto& file : files) {
    	if(file.name==destName)
    		deleteFile(destName);
    	}
        for (const auto& file : files) {
            if (file.name == srcName) {
                createFile(destName, file.size);
                writeFile(destName,  string(disk + file.start, disk + file.start + file.size));
                 cout << "Файл " << srcName << " успешно скопирован в " << destName << ".\n";
                return;
            }
        }
         cout << "Ошибка: исходный файл " << srcName << " не найден.\n";
    }

    void moveFile(const  string& srcName, const  string& destName) {
        for (auto& file : files) {
            if (file.name == srcName) {
                file.name = destName;
                 cout << "Файл " << srcName << " успешно переименован в " << destName << "\n";
                return;
            }
        }
         cout << "Ошибка: файл " << srcName << " не найден\n";
    }

    void createDump(const  string& dumpFileName) {
         ofstream dumpFile(dumpFileName);
        if (!dumpFile.is_open()) {
             cout << "Ошибка: не удалось создать дамп-файл " << dumpFileName << ".\n";
            return;
        }

        dumpFile << "Файловая система (размер: " << DISK_SIZE << " байт)\n";
        dumpFile << "Свободное место: " << freeSpace << " байт\n\n";

        dumpFile << "Список файлов:\n";
        for (const auto& file : files) {
            dumpFile << "Имя: " << file.name
                     << ", Начало: " << file.start
                     << ", Размер: " << file.size << " байт\n";
        }

        dumpFile << "\nСодержимое диска:\n";
        for (int i = 0; i < DISK_SIZE; i++) {
            if (disk[i] == '\0') {
                dumpFile << '.';
            } else {
                dumpFile << disk[i];
            }
            if ((i + 1) % 50 == 0) {
                dumpFile << '\n';
            }
        }

        dumpFile.close();
         cout << "Дамп файловой системы успешно создан: " << dumpFileName << "\n";
    }
};

int main() {
    FileSystem fs;

    fs.createFile("1", 100);
    fs.writeFile("1", "Hello, World!");
    fs.readFile("1");

    fs.createFile("2", 50);
    fs.copyFile("1", "2");
    fs.readFile("2");

    fs.moveFile("2", "3");
    fs.readFile("3");

    fs.deleteFile("1");
    fs.createDump("filesystem_dump.txt");
    return 0;
}
