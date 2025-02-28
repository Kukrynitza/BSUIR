from typing import TypedDict
from human import Human


class DiplomaProjectDict(TypedDict):
    presentation: int
    report: int


class ScientificDirector(Human):
    def add_scientific_director(self):
        self.add_human()
        print(f"Научный руководитель {self._last_name} {self._first_name} {self._surname} добавлен!")

    @staticmethod
    def verification_of_the_graduation_project(diploma: DiplomaProjectDict) -> bool:
        if diploma['presentation'] <= 75:
            print(f'Надо доделать презентацию, полнота раскрытия темы {diploma['presentation']}%')
            return False
        if diploma['report'] <= 80:
            print(f'Надо доделать доклад, полнота раскрытия темы {diploma['report']}% ')
            return False
        print('Все хорошо, можно показывать')
        return True

    def get_first_name(self) -> str:
        return self._first_name

    def get_surname(self) -> str:
        return self._surname

    def is_exist(self) -> bool:
        if self._surname:
            return True
        return False
