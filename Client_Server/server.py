import argparse
import pickle
import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from log.server_log_config import logger


def server_connect(ip_start="", tcp_start=7777):
    """Развертывание сервера на определнном ip и tcp"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((ip_start, tcp_start))
    sock.listen(5)
    return sock


def server_to_accept(sock_cli):
    """Поставить сервер на ожидание клиента"""
    client, address = sock_cli.accept()
    return client, address


def start_parser(func_start):
    """Сценарий для терминала"""
    parser = argparse.ArgumentParser(description='Запуск сервера')
    parser.add_argument("-a", type=str, help='Выбор ip')
    parser.add_argument("-p", type=int, help='Выбор tcp')
    args = parser.parse_args()
    if args.a and args.p is not None:
        func_start(ip_go=args.a, tcp_go=args.p)
    elif args.a is None:
        func_start(tcp_go=args.p)
    elif args.p is None:
        func_start(ip_go=args.a)
    else:
        func_start()


def ser_send_p(sock_cli, base_cli):
    """Отправка сообщений пользователям"""
    sock_cli.send(pickle.dumps(str(f"Список клиентов: {base_cli}")))
    data = sock_cli.recv(1024)
    data_message = pickle.loads(data)
    try:
        logger.info(f'{data_message}')
    except Exception as ex:
        logger.info(f'Произошел сбой: {ex}')

    if int(data_message[0].strip("#")) <= 100:
        base_cli[data_message[0]].send(pickle.dumps(data_message[1]))


def ser_send_g(sock_cli, base_gro):
    """Отправка сообщений группе"""
    sock_cli.send(pickle.dumps(str(f"Список групп: {base_gro}")))
    data = sock_cli.recv(1024)
    data_message = pickle.loads(data)
    if int(data_message[0].strip("#")) >= 100:
        for sock_cl in base_gro[data_message[0]]:
            sock_cl.send(pickle.dumps(str(data_message[1])))


def ser_add_g(sock_cli, base_gro):
    """Создание или добавление группы"""
    sock_cli.send(pickle.dumps(str(f"Список групп: {base_gro}")))
    data = sock_cli.recv(1024)
    data_message = pickle.loads(data)
    if data_message in base_gro:
        for k, v in base_gro.items():
            if k == data_message:
                if sock_cli in v:
                    sock_cli.send(pickle.dumps("Вы уже создали или добавились в группу"))
                    break
                elif sock_cli not in v:
                    v.append(sock_cli)
                    base_gro.update({data_message: v})
                    sock_cli.send(pickle.dumps("Вы успешно добавились в группу"))
                    break
    elif int(data_message.strip("#")) >= 100:
        base_gro.update({data_message: [sock_cli]})
        sock_cli.send(pickle.dumps("Вы успешно создали группу"))


def ser_run(sock_cli, base_cli, base_gro, func_p, func_g, func_add):
    """Запуск внутренего сцеанрия сервера"""
    while True:
        data = sock_cli.recv(1024)
        data_message = pickle.loads(data)
        if data_message == "П":
            # func_p(sock_cli,base_cli)
            p_send_p = Thread(target=func_p, args=(sock_cli, base_cli))
            p_send_p.start()
        elif data_message == "Г":
            p_send_g = Thread(target=func_g, args=(sock_cli, base_gro))
            p_send_g.start()
        elif data_message == "ВГ":
            p_add_g = Thread(target=func_add, args=(sock_cli, base_gro))
            p_add_g.start()


def server_original(ip_go="", tcp_go=7777):
    """Запуск сервера"""
    sock = server_connect(ip_go, tcp_go)
    clients = []
    base_group = {}

    while True:
        try:
            cli, adr = server_to_accept(sock)
        except OSError:
            pass
        else:
            print(f"Получен запрос на соединение от {adr}")
            clients.append(cli)
        finally:
            wait = 10
            w = []
            try:
                r, w, er = select.select([], clients, [], wait)
            except Exception as err:
                print(f"Клиент отключился{err}")

            base_all_client = {f'#{a}': clients[a] for a in range(len(clients))}

            for s in w:
                # ser_run(s, base_all_client, base_group, ser_send_p, ser_send_g, ser_add_g)
                t_st = Thread(target=ser_run,
                              args=(s, base_all_client, base_group, ser_send_p, ser_send_g, ser_add_g))
                t_st.start()


if __name__ == "__main__":
    try:
        start_parser(server_original)
    except Exception as e:
        start_parser(server_original())
        logger.info(e)
