import subprocess

from log.serverlogconfig import logger


def info_log(mod):
    """
    Функция для просмотра модуля отработки

        Параметры:
            mod (str): модуль.
        Возвращаемое значение:
            None: Функция ничего не возвращает.
    """
    logger.info(f"Сообщение от клиента: модуль {mod} отработал")


def log_send(data_mes):
    """
    Запись в log

        Параметры:
            data_mes (str) : Сообщение которое будет передано в лог.
        Возвращаемое значение:ничего не возвращает
            None: Функция ничего не возвращает.
    """
    try:
        logger.info(f"{data_mes}")
    except Exception as e:
        logger.info(f"Произошел сбой: {e}")


def main(func_ser_cli):
    """
    Функция для просмотра функции модуля отработки

        Параметры:
            func_ser_cli : Функция модуля которая стала аргументом в нашей функции .
        Возвращаемое значение:
            None: Функция ничего не возвращает.
    """
    logger.info(f"Функция {func_ser_cli.__name__} вызвана из функции {main.__name__}")
    func_ser_cli("127.0.0.1", 7777)


def client_start_3(n=3):
    """
    Функция, для запуска множества клиентов на сервер

        Параметры:
            ip_go (str): ip сервера к которому подключаемся.
            tcp (int): tcp сервера к которому подключаемся.
            n (int): n количество запущенных клиентов.
        Возвращаемое значение:
            None: Функция ничего не возвращает
    """
    for i in range(0, n):
        subprocess.Popen(
            f"lxterminal -t sample{i} -e bash -c 'python3 client.py ; read v '",
            shell=True,
        )


def login_required(func):
    """
    Функция для запрета входа в определенные части функционала, только для определенных пользователей

        Параметры:
            func: Функция которую мы будем ограждать от чужого входа.
        Возвращаемое значение:
            Function: Функция возвращает функцию.
    """

    def wrapper(*args):
        if args[1] == "Groofi":
            print("Доступ разрешен")
            func(args[0], args[1])
        else:
            print("Доступно только Groofi")
            func(args[0], "Доступно только Groofi")

    return wrapper


if __name__ == "__main__":
    pass
