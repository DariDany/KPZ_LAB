def check_number_range(number):
    if number < 0:
        return "Від'ємне число"
    else:
        if 0 <= number <= 10:
            return "Число від 0 до 10"
        else:
            if 11 <= number <= 20:
                return "Число від 11 до 20"
            else:
                return "Число більше 20"


def process_numbers():
    # Фіксований список чисел
    numbers = [5, -3, 12, 25, 8, 19]

    # Обробка всіх чисел за допомогою for i in range(a, b)
    for i in range(0, len(numbers)):  # цикл по індексах списку
        number = numbers[i]
        result = check_number_range(number)
        print(f"Число {number} - {result}")

    # Вкладені цикли для виведення таблиці множення
    print("\nТаблиця результатів:")
    for i in range(0, len(numbers)):  # цикл по індексах списку
        number = numbers[i]
        for j in range(1, 6):  # цикл для множення
            print(f"{number} x {j} = {number * j}")
        print("---------")


# Запуск програми
process_numbers()
