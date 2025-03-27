class HashTable:
    def __init__(self, size=20, expand_step=3):
        self.size = size
        self.expand_step = expand_step
        self.table = [{"ID": None, "C": 0, "U": 0, "T": 0, "L": 0, "D": 0, "P0": None, "Pi": None} for _ in range(size)]

    def _hash(self, key):
        return sum(ord(char) for char in key) % self.size

    def _expand_table(self):
        self.table.extend([{"ID": None, "C": 0, "U": 0, "T": 0, "L": 0, "D": 0, "P0": None, "Pi": None} for _ in range(self.expand_step)])
        self.size += self.expand_step
        print(f" Таблица расширена на {self.expand_step} ячеек. Новый размер: {self.size}")

    def insert(self, key, data):
        h = self._hash(key)
        for i in range(self.size):
            index = (h + i) % self.size
            if self.table[index]["U"] == 0 or self.table[index]["D"] == 1:
                self.table[index] = {"ID": key, "C": int(i > 0), "U": 1, "T": 0, "L": 0, "D": 0, "P0": None, "Pi": data}
                print(f" {key} добавлен в ячейку {index}")
                return
        self._expand_table()
        self.insert(key, data)

    def search(self, key):
        results = []
        for i, row in enumerate(self.table):
            if row["U"] == 1 and row["ID"] == key and row["D"] == 0:
                results.append((i, row["Pi"]))
        if results:
            print(f" Найдено {len(results)} записей с фамилией {key}:")
            for index, data in results:
                print(f"   - Ячейка {index}: {data}")
        else:
            print(" Не найдено")

    def delete(self, key):
        deleted_count = 0
        for i, row in enumerate(self.table):
            if row["U"] == 1 and row["ID"] == key:
                self.table[i] = {"ID": None, "C": 0, "U": 0, "T": 0, "L": 0, "D": 0, "P0": None, "Pi": None}
                deleted_count += 1
                print(f" {key} удалён из ячейки {i}")
        if deleted_count == 0:
            print(f" {key} не найден")
        else:
            print(f" Удалено {deleted_count} записей с фамилией {key}")

    def display(self):
        print(f"\n{'№':<3} {'ID':<10} {'C':<2} {'U':<2} {'T':<2} {'L':<2} {'D':<2} {'P0':<3} {'Pi':<10}")
        print("-" * 40)
        for i, row in enumerate(self.table):
            print(f"{i:<3} {row['ID'] or '-':<10} {row['C']:<2} {row['U']:<2} {row['T']:<2} {row['L']:<2} {row['D']:<2} {row['P0'] or '-':<3} {row['Pi'] or '-':<10}")
        print("-" * 40)