from pydantic import BaseModel, Field, ValidationError, validator
import re


class Schema(BaseModel):
    name: str = Field(...)

    @validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Поле не может быть пустым!")
        if len(value) < 2:
            raise ValueError("Введите больше 2 символов!")
        if len(value) > 30:
            raise ValueError("Введите меньше 30 символов!")
        if not re.match(r'^[А-ЯЁа-яё]+$', value):
            raise ValueError("Можно вводить только русские буквы!")
        return value


class Human:
    _first_name: str
    _last_name: str
    _surname: str

    @staticmethod
    def _get_valid_input(field_name: str) -> str:
        while True:
            value = input(f"Введите {field_name}: ").strip()
            try:
                validated_data = Schema(name=value)
                return validated_data.name
            except ValidationError as e:
                err = e.errors()[0]["msg"].split(', ')[1]
                print(err)

    def add_human(self):
        self._last_name: str = self._get_valid_input("Фамилия")
        self._first_name: str = self._get_valid_input("Имя")
        self._surname: str = self._get_valid_input("Отчество")
