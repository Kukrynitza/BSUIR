import random
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import string
from datetime import datetime, timedelta


class PasswordAnalyzer:
    def __init__(self):
        random.seed(time.time())
        self.alphabet = '0123456789'

    def generate_digital_string(self, length):
        return ''.join(random.choices(self.alphabet, k=length))

    def analyze_frequency(self, text):
        total_chars = len(text)
        counter = Counter(text)

        print("\n" + "=" * 50)
        print("АНАЛИЗ ЧАСТОТНОГО РАСПРЕДЕЛЕНИЯ")
        print("=" * 50)
        print(f"Длина строки: {total_chars} символов")
        print("\nСимвол | Количество | Частота (%)")
        print("-" * 35)

        for char in sorted(counter.keys()):
            count = counter[char]
            percentage = (count / total_chars) * 100
            print(f"   {char}   | {count:9d}  | {percentage:6.2f}%")

        self.plot_frequency_distribution(counter, total_chars)

        self.check_uniformity(counter, total_chars)

    def plot_frequency_distribution(self, counter, total_chars):
        chars = sorted(counter.keys())
        counts = [counter[char] for char in chars]
        percentages = [(count / total_chars) * 100 for count in counts]

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        bars = plt.bar(chars, counts, color='skyblue', edgecolor='black')
        plt.xlabel('Цифры')
        plt.ylabel('Количество')
        plt.title('Распределение цифр в строке')

        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     f'{count}', ha='center', va='bottom')

        plt.subplot(1, 2, 2)
        plt.pie(percentages, labels=chars, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Процентное распределение')

        plt.tight_layout()
        plt.show()

    def check_uniformity(self, counter, total_chars):
        expected = total_chars / len(self.alphabet)
        chi_square = 0

        for char in self.alphabet:
            observed = counter.get(char, 0)
            chi_square += (observed - expected) ** 2 / expected

        print(f"\nПроверка равномерности (χ²): {chi_square:.3f}")
        if chi_square < 15:
            print("Распределение близко к равномерному")
        else:
            print("Распределение неравномерное")

    def brute_force_simulation(self, password, max_attempts=1000000):
        attempts = 0
        current_guess = '0' * len(password)
        start_time = time.time()

        print(f"\nНачинаем подбор пароля: {password}")

        while current_guess != password and attempts < max_attempts:
            attempts += 1

            guess_list = list(current_guess)
            for i in range(len(guess_list) - 1, -1, -1):
                if guess_list[i] < '9':
                    guess_list[i] = str(int(guess_list[i]) + 1)
                    break
                else:
                    guess_list[i] = '0'
            current_guess = ''.join(guess_list)

        end_time = time.time()
        time_taken = end_time - start_time

        if attempts >= max_attempts:
            print(f"Достигнуто максимальное количество попыток ({max_attempts})")
        else:
            print(f"Пароль подобран за {attempts} попыток")
            print(f"Время подбора: {time_taken:.6f} секунд")

        return time_taken, attempts

    def calculate_estimated_time(self, password_length):
        total_combinations = 10 ** password_length

        test_password = '0' * password_length
        test_time, _ = self.brute_force_simulation(test_password, 1000)

        attempts_per_second = 1000 / test_time if test_time > 0 else 1000

        estimated_time = total_combinations / attempts_per_second

        print(f"\nТеоретическая оценка для пароля длины {password_length}:")
        print(f"Всего комбинаций: {total_combinations:,}")
        print(f"Скорость перебора: {attempts_per_second:,.0f} попыток/сек")
        print(f"Оценочное время: {estimated_time:.2f} секунд")

        if estimated_time > 60:
            minutes = estimated_time / 60
            if minutes > 60:
                hours = minutes / 60
                if hours > 24:
                    days = hours / 24
                    if days > 365:
                        years = days / 365
                        print(f"Примерно {years:.1f} лет")
                    else:
                        print(f"Примерно {days:.1f} дней")
                else:
                    print(f"Примерно {hours:.1f} часов")
            else:
                print(f"Примерно {minutes:.1f} минут")

        return estimated_time

    def plot_time_vs_length(self, max_length=8, samples=3):
        lengths = list(range(1, max_length + 1))
        avg_times = []

        print("\n" + "=" * 60)
        print("ПОСТРОЕНИЕ ГРАФИКА ЗАВИСИМОСТИ ВРЕМЕНИ ОТ ДЛИНЫ ПАРОЛЯ")
        print("=" * 60)
        print("Длина | Среднее время (сек) | Теор. время (сек)")
        print("-" * 50)

        for length in lengths:
            times = []
            for _ in range(samples):
                password = self.generate_digital_string(length)
                time_taken, _ = self.brute_force_simulation(password, 100000)
                times.append(time_taken)

            avg_time = np.mean(times)
            avg_times.append(avg_time)

            theoretical_time = self.calculate_estimated_time(length)

            print(f"{length:5d} | {avg_time:18.6f} | {theoretical_time:18.2f}")

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.plot(lengths, avg_times, 'o-', linewidth=2, markersize=8)
        plt.xlabel('Длина пароля')
        plt.ylabel('Среднее время подбора (сек)')
        plt.title('Зависимость времени подбора от длины пароля')
        plt.grid(True, alpha=0.3)
        plt.yscale('log')

        plt.subplot(1, 2, 2)
        theoretical_times = [10 ** l for l in lengths]
        plt.plot(lengths, theoretical_times, 's-', color='red', linewidth=2, markersize=8)
        plt.xlabel('Длина пароля')
        plt.ylabel('Теоретическое время (сек, лог)')
        plt.title('Экспоненциальный рост сложности')
        plt.yscale('log')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        return lengths, avg_times


def main():
    analyzer = PasswordAnalyzer()

    while True:
        print("\n" + "=" * 60)
        print("АНАЛИЗАТОР ПАРОЛЕЙ ИЗ АРАБСКИХ ЦИФР")
        print("=" * 60)
        print("1. Сгенерировать строку и проанализировать распределение")
        print("2. Протестировать подбор конкретного пароля")
        print("3. Построить график зависимости времени от длины")
        print("4. Теоретическая оценка времени подбора")
        print("5. Выход")

        choice = input("Выберите опцию (1-5): ").strip()

        if choice == '1':
            try:
                length = int(input("Введите длину строки: "))
                if length <= 0:
                    print("Длина должна быть положительным числом!")
                    continue

                digital_str = analyzer.generate_digital_string(length)
                print(f"Сгенерированная строка: {digital_str}")
                analyzer.analyze_frequency(digital_str)

            except ValueError:
                print("Пожалуйста, введите целое число!")

        elif choice == '2':
            try:
                length = int(input("Введите длину пароля для подбора: "))
                if length <= 0:
                    print("Длина должна быть положительным числом!")
                    continue

                password = analyzer.generate_digital_string(length)
                print(f"Тестовый пароль: {password}")
                analyzer.brute_force_simulation(password)

            except ValueError:
                print("Пожалуйста, введите целое число!")

        elif choice == '3':
            try:
                max_length = int(input("Максимальная длина для анализа (1-8): "))
                max_length = min(max(1, max_length), 8)
                samples = int(input("Количество образцов на длину (1-5): "))
                samples = min(max(1, samples), 5)

                analyzer.plot_time_vs_length(max_length, samples)

            except ValueError:
                print("Пожалуйста, введите целое число!")

        elif choice == '4':
            try:
                length = int(input("Введите длину пароля для теоретической оценки: "))
                if length <= 0:
                    print("Длина должна быть положительным числом!")
                    continue

                analyzer.calculate_estimated_time(length)

            except ValueError:
                print("Пожалуйста, введите целое число!")

        elif choice == '5':
            print("Выход из программы...")
            break

        else:
            print("Неверный выбор! Пожалуйста, выберите от 1 до 5.")


if __name__ == "__main__":
    main()