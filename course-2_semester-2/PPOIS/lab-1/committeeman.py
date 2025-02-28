import random
from human import Human


class Committeeman(Human):
    __profession: str
    __difficulty_to_pass: int

    def add_committeeman(self):
        self.add_human()
        self.__profession = self._get_valid_input("Профессия")
        self.__difficulty_to_pass = random.randrange(80, 100, 1)
        print(
            f"{self.__profession} "f"{self._last_name} {self._first_name} {self._surname} добавлен"
            f"(сложность прохождения {self.__difficulty_to_pass}%)!"
        )

    def get_difficulty(self) -> int:
        return self.__difficulty_to_pass
