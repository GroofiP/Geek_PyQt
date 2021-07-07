import argparse
import multiprocessing
import pickle
from socket import socket, AF_INET, SOCK_STREAM
from log.server_log_config import logger


def client_connect(ip_start="", tcp_start=7777):
    """Подключение клиента на определнном ip и tcp"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((ip_start, tcp_start))
    return sock


def start_client_parser(func_start):
    """Сценарий для терминала"""
    parser = argparse.ArgumentParser(description='Запуск клиента')
    parser.add_argument("a", type=str, help='Выбор ip', nargs='?')
    parser.add_argument("p", type=int, help='Выбор tcp', nargs='?')
    args = parser.parse_args()
    if args.a and args.p is not None:
        func_start(args.a, args.p)
    else:
        func_start()


def cli_start(sock):
    """Выбор сценария на сервере"""
    msg = input(
        'Введите, что вы хотите сделать (П/Отправить сообщение пользователю, '
        'Г/Отправить группе, ВГ/Вступить в группу)? '
    )
    sock.send(pickle.dumps(msg))
    return msg


def log_send(data_mes):
    "Запись в log"
    try:
        logger.info(f'{data_mes}')
    except Exception as e:
        logger.info(f'Произошел сбой: {e}')


def cli_rec(sock):
    """Проверка сообщений от сервера"""
    data_message = pickle.loads(sock.recv(1024))
    print(f"\nСообщение:{data_message}")
    log_send(data_message)


def cli_send_p(sock):
    """Отправка сообщений пользователям"""
    msg_a = input("Введите номер пользователя с #0 до #99 с которым хотите начать беседу: ")
    msg_b = input(f'Введите сообщение пользователю {msg_a}:')
    sock.send(pickle.dumps([msg_a, msg_b]))


def cli_send_g(sock):
    """Отправка сообщений группе"""
    msg_a = input("Введите номер группы с #100 до #999 с которым хотите начать беседу: ")
    msg_b = input(f'Введите сообщение пользователю {msg_a}:')
    sock.send(pickle.dumps([msg_a, msg_b]))


def cli_add_g(sock):
    """Создание или добавление группы"""
    msg_a = input("Введите номер группы от #100 которую хотите создать или подключится: ")
    sock.send(pickle.dumps(msg_a))


def client_original(ip_go="", tcp_go=7777):
    """Запуск клиента"""
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((ip_go, tcp_go))
        while True:
            p_1 = multiprocessing.Process(target=cli_rec, args=(s,))
            p_1.start()
            msg_1 = cli_start(s)
            if msg_1 == 'П':
                cli_send_p(s)
            elif msg_1 == 'Г':
                cli_send_g(s)
            elif msg_1 == 'ВГ':
                cli_add_g(s)
            else:
                pass


if __name__ == '__main__':
    try:
        start_client_parser(client_original)
    except Exception as e:
        start_client_parser(client_original())
        logger.info(e)
