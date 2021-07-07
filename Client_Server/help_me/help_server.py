import pickle
import select

from Client_Server.dec import logs
from Client_Server.log.server_log_config import logger
from Client_Server.server import server_connect, server_to_accept
from Client_Server.service import info_log


def server_to_accept_message(cli_add):
    """Прием сообщения от клиента и просмотр этого сообщения """
    data = cli_add.recv(1024)
    data_message = pickle.loads(data)
    try:
        logger.info(f'Сообщение от клиента {cli_add.getpeername()}: {data_message}')
    except Exception as err:
        logger.info(f'Произошел сбой: {err}')
    return f'Сообщение от клиента {cli_add.getpeername()}: {data_message}'


def server_send(cli_add, message):
    """Отправка сообщения"""
    cli_add.send(pickle.dumps(message))


@logs
def server_start(ip_go="", tcp_go=7777):
    """Функция для настройки сервера под ключ"""
    sock = server_connect(ip_go, tcp_go)
    while True:
        client, address = server_to_accept(sock)
        message = server_to_accept_message(client)
        server_send(client, message)
        info_log("server")
        client.close()


def read_requests(r_clients, all_clients):
    """Чтение запросов из списка клиентов для эхо сервера"""
    responses = {}
    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            responses[sock] = data
        except OSError:
            print(f'Клиент {sock.getpeername()} отключился.')
            all_clients.remove(sock)
    return responses


def write_responses(requests, w_clients, all_clients, func_proc_res):
    """ Эхо-ответ сервера клиентам, от которых были запросы"""
    for sock in w_clients:
        if sock in requests:
            try:
                func_proc_res(requests, sock, w_clients)
            except OSError:
                print(f'Клиент {sock.getpeername()} отключился.')
                all_clients.remove(sock)


def write_responses_ver_1(*args):
    resp = args[0][args[1]].encode('utf-8')
    for cli in args[2]:
        cli.send(resp)


def write_responses_ver_2(*args):
    resp = args[0][args[1]]
    print(f"{resp}")


def echo_server_select(x_socket, x_cli, func_proc_select):
    while True:
        try:
            cli, adr = server_to_accept(x_socket)
        except OSError:
            pass
        else:
            print(f"Получен запрос на соединение от {adr}")
            x_cli.append(cli)
        finally:
            # Проверить наличие событий ввода-вывода
            wait = 10
            r = []
            w = []
            try:
                r, w, er = select.select(x_cli, x_cli, [], wait)
            except Exception as err:
                print(f"Клиент отключился{err}")

            requests = read_requests(r, x_cli)  # Сохраним запросы клиентов
            if requests:
                write_responses(requests, w, x_cli, func_proc_select)  # Выполним отправку ответов клиентам


def echo_server(ip_go="", tcp_go=7777, func_proc=write_responses_ver_1):
    """Функция для настройки эхо сервера под ключ"""
    clients = []
    sock = server_connect(ip_go, tcp_go)
    print(sock)
    echo_server_select(sock, clients, func_proc)
