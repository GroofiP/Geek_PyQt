import os
from multiprocessing import Process


def doubler(num):
    """
    Функция умножитель на два
    """
    result = num * 2
    proc_id = os.getpid()
    print(f'{number} умноженное на 2 будет {result}.\nЭто был процесс: {proc_id}')


if __name__ == '__main__':
    numbers = [5, 10, 15, 20, 25]
    proc_all = []

    for index, number in enumerate(numbers):
        proc = Process(target=doubler, args=(number,))
        proc_all.append(proc)
        proc.start()
