import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass
class Pixel:
    point: Point
    intensity: float = 1.0


def generate(x0, y0, x1, y1):
    """Генерация точек гиперболы"""
    # Определяем размеры области
    width = abs(x1 - x0)
    height = abs(y1 - y0)

    # Параметры гиперболы
    a = max(width // 4, 2)  # Полуось по X
    b = max(height // 4, 2)  # Полуось по Y

    # Центр гиперболы
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2

    # Рисуем две ветви гиперболы (x^2/a^2 - y^2/b^2 = 1)
    points = []

    # Первая ветвь (x > 0)
    x = a
    while x <= width // 2:
        # y = b * sqrt((x^2 / a^2) - 1)
        y_squared = (x * x) / (a * a) - 1
        if y_squared >= 0:
            y = int(b * math.sqrt(y_squared))

            # Добавляем точки для всех квадрантов
            if y > 0:
                points.append(Pixel(Point(cx + x, cy + y)))
                points.append(Pixel(Point(cx + x, cy - y)))
                points.append(Pixel(Point(cx - x, cy + y)))
                points.append(Pixel(Point(cx - x, cy - y)))
        x += 1

    # Вторая ветвь (y > 0) - для более полного заполнения
    y = b
    while y <= height // 2:
        # x = a * sqrt(1 + (y^2 / b^2))
        x_squared = 1 + (y * y) / (b * b)
        x = int(a * math.sqrt(x_squared))

        if x <= width // 2:
            points.append(Pixel(Point(cx + x, cy + y)))
            points.append(Pixel(Point(cx + x, cy - y)))
            points.append(Pixel(Point(cx - x, cy + y)))
            points.append(Pixel(Point(cx - x, cy - y)))
        y += 1

    return points

name = "Гипербола"