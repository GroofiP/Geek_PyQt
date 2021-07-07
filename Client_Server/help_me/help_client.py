import pickle
from socket import socket, AF_INET, SOCK_STREAM

from Client_Server.dec import logs
from Client_Server.log.server_log_config import logger
from Client_Server.service import info_log


def client_connect(ip_start="", tcp_start=7777):
    """Подключение клиента на определнном ip и tcp"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((ip_start, tcp_start))
    return sock


def client_to_accept_message(sock_cli):
    """Прием сообщения от сервера и просмотр этого сообщения """
    data = sock_cli.recv(1024)
    data_message = pickle.loads(data)
    try:
        logger.info(f'{data_message}')
    except Exception as e:
        logger.info(f'Произошел сбой: {e}')
    print(f'{data_message}')


def client_send(sock_cli):
    """Отправка сообщения"""
    message = {f"{sock_cli.getsockname()}": input("Введите сообщение от клиента: ")}
    if message == "":
        return False
    sock_cli.send(pickle.dumps(message))


@logs
def client_start(ip_go="", tcp_go=7777):
    """Функция для настройки клиента под ключ"""
    sock = client_connect(ip_go, tcp_go)
    while True:
        client_send(sock)
        client_to_accept_message(sock)
        info_log("client")


def echo_client(ip_go="", tcp_go=7777):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((ip_go, tcp_go))
        while True:
            msg = input('Введите сообщение: ')
            if msg == 'exit':
                break
            elif msg == "":
                data = s.recv(1024).decode('utf-8')
                print(f'{data}')
            else:
                massage = f"Сообщение от {s.getsockname()}: {msg}\n"
                s.send(massage.encode('utf-8'))  # Отправить!
                data = s.recv(1024).decode('utf-8')
                print(f'{data}')


def echo_client_main(ip_go="", tcp_go=7777):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((ip_go, tcp_go))
        print(s)
        while True:
            msg = input('Введите сообщение: ')
            if msg == 'exit':
                break
            msg = f"Сообщение от {s.getsockname()}: {msg}\n"
            s.send(msg.encode('utf-8'))
