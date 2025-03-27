import unittest
from unittest.mock import patch
from hash_table import HashTable


class TestHashTable(unittest.TestCase):
    def setUp(self):
        self.ht = HashTable()

    def test_insert_and_search(self):
        self.ht.insert("Ivanov", "Ivan")
        with patch("builtins.print") as mock_print:
            self.ht.search("Ivanov")
        mock_print.assert_any_call(" Найдено 1 записей с фамилией Ivanov:")

    def test_insert_collision_handling(self):
        self.ht.insert("Smith", "John")
        self.ht.insert("htimS", "Jane")  # Может вызвать коллизию

        with patch("builtins.print") as mock_print:
            self.ht.search("Smith")
        mock_print.assert_any_call(" Найдено 1 записей с фамилией Smith:")

        with patch("builtins.print") as mock_print:
            self.ht.search("htimS")
        mock_print.assert_any_call(" Найдено 1 записей с фамилией htimS:")

    def test_delete_entry(self):
        self.ht.insert("Petrov", "Petr")
        with patch("builtins.print") as mock_print:
            self.ht.delete("Petrov")
        mock_print.assert_any_call(" Petrov удалён из ячейки 0")
        mock_print.assert_any_call(" Удалено 1 записей с фамилией Petrov")

        with patch("builtins.print") as mock_print:
            self.ht.search("Petrov")
        mock_print.assert_any_call(" Не найдено")

    def test_expand_table(self):
        initial_size = self.ht.size
        for i in range(25):
            self.ht.insert(f"User{i}", "Data")
        self.assertGreater(self.ht.size, initial_size)  # Проверка, что размер увеличился


if __name__ == "__main__":
    unittest.main()

# coverage run -m unittest discover
# coverage report -m
