def check_number_range(number):
    if number < 0:
        return "Отрицательное число"
    else:
        if 0 <= number <= 10:
            return "Число от 0 до 10"
        else:
            if 11 <= number <= 20:
                return "Число от 11 до 20"
            else:
                return "Число больше 20"


def process_numbers():
    numbers = []
    while True:
        try:
            num = int(input("Введите число (или 'q' для выхода): "))
            numbers.append(num)
        except ValueError:
            print("Неверный ввод. Введите целое число.")

        cont = input("Хотите продолжить? (y/n): ")
        if cont.lower() != 'y':
            break

    # Обрабатываем все введенные числа
    for number in numbers:
        result = check_number_range(number)
        print(f"Число {number} - {result}")

    # Вложенные циклы для вывода результатов
    print("\nТаблица результатов:")
    for number in numbers:
        for i in range(1, 6):
            print(f"{number} x {i} = {number * i}")
        print("---------")


# Запуск программы
process_numbers()
