import subprocess

from log.server_log_config import logger


def info_log(mod):
    logger.info(f'Сообщение от клиента: модуль {mod} отработал')


def main(func_ser_cli):
    logger.info(f"Функция {func_ser_cli.__name__} вызвана из функции {main.__name__}")
    func_ser_cli("127.0.0.1", 7777)


def client_start_3(n=3):
    """
    Функция, для запуска множества клиентов на сервер

        Параметры:
            n (int): n количество запущенных клиентов.
        Возвращаемое значение:
            None: Функция ничего не возвращает
    """
    for i in range(0, n):
        subprocess.Popen(f"lxterminal -t sample{i} -e bash -c 'python3 client.py ; read v '", shell=True)


if __name__ == "__main__":
    client_start_3()
