import argparse
import dis
import json
import select
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from storage_sqlite import Storage, PATH
from service import log_send


#
# a) клиент:
# * логин;
# * информация.

class PortVerifier:
    def __init__(self, tcp):
        self.tcp = tcp

    def __setattr__(self, key, value):
        if not isinstance(value, int):
            raise TypeError(f"Значение должно быть типа {int}")
        super().__setattr__(key, value)


class ServerVerifier(type):

    def __init__(self, name_class, bases, dict_class):
        for key, value in dict_class.items():
            a = dis.code_info(value)
            if "connect" in a:
                raise Exception("Такого метода как 'connect' не должно быть в классе")
            elif key == "server_con":
                if "SOCK_STREAM" not in a:
                    raise Exception(
                        "Такая функция у сокета,как 'SOCK_STREAM' должна быть в классе, так как соединение должно быть TCP")
        type.__init__(self, name_class, bases, dict_class)


class Server(metaclass=ServerVerifier):
    def __init__(self, ip, tcp):
        self.ip = ip
        self.tcp = PortVerifier(tcp).tcp
        self.sock = self.server_con()

    def server_con(self):
        """Развертывание сервера на определенном ip и tcp"""
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.ip, self.tcp))
        sock.listen(5)
        return sock

    @staticmethod
    def auth_server(sock_cli):
        auth = json.loads(sock_cli.recv(1024).decode("utf-8"))
        base_data = Storage(PATH, "users")
        try:
            check_base = base_data.view_table()
        except Exception as ex:
            log_send(ex)
            check_base = ""
        if auth not in check_base:
            sock_cli.send(json.dumps(True, ensure_ascii=False).encode("utf-8"))
            info = json.loads(sock_cli.recv(1024).decode("utf-8"))
            base_data = Storage(PATH, "users", auth, info)
            base_data.add_base()
            base_data.metadata.clear()
        else:
            sock_cli.send(json.dumps("Вы авторизованы", ensure_ascii=False).encode("utf-8"))
        check_base = base_data.view_table_all()
        for id_auth in check_base:
            if id_auth[1] == auth:
                return id_auth[0]

    @staticmethod
    def history_client(sock_cli, id_auth):
        time = datetime.today().strftime("%Y.%m.%d %H:%M:%S")
        ip_date = sock_cli.getpeername()
        base_data = Storage(PATH, "histories_users", login=id_auth, date=time, ip_date=ip_date)
        base_data.metadata.clear()
        base_data.add_base()
        base_data.view_table_all()
        base_data.view_table_main("histories_users")

    @staticmethod
    def ser_send_p(sock_cli, base_cli, func_base):
        """Отправка сообщений пользователям"""
        sock_cli.send(json.dumps(str(f"Список клиентов: {base_cli}"), ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
        log_send(data_message)
        try:
            if int(data_message[0].strip("#")) <= 100:
                sock_recv = base_cli[data_message[0]]
                base_cli[data_message[0]].send(json.dumps(data_message[1], ensure_ascii=False).encode("utf-8"))
                func_base(sock_cli, sock_recv)
        except Exception as ex:
            sock_cli.send(
                json.dumps(f"Сообщение испорчено, попробуйте отослать ещё раз! ", ensure_ascii=False).encode("utf-8"))
            log_send(ex)

    @staticmethod
    def add_contacts(sock_cli_send, sock_cli_recv):
        send_cli_s = sock_cli_send.getpeername()
        send_cli_r = sock_cli_recv.getpeername()
        base_data = Storage(PATH, "contacts")
        base_data.metadata.clear()
        result = base_data.view_table_main("histories_users")
        list_id_send = []
        list_id_recv = []
        for a in result:
            print(type(a[3]),type(send_cli_s))
            if str(a[3]) == str(send_cli_s):
                print(a[1])
                list_id_send.append(a[1])
            elif str(a[3]) == str(send_cli_r):
                print(a[1])
                list_id_recv.append(a[1])
        print(list_id_recv,list_id_send)
        base_data = Storage(PATH, "contacts", login=list_id_send[0], login_recv=list_id_recv[0])
        base_data.add_base()
        result = base_data.view_table_main("contacts")
        for a in result:
            print(a)

    @staticmethod
    def ser_send_g(sock_cli, base_gro):
        """Отправка сообщений группе"""
        sock_cli.send(json.dumps(str(f"Список групп: {base_gro}"), ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
        if str(data_message[0].strip("#")).isdigit():
            if int(data_message[0].strip("#")) >= 100:
                for sock_cl in base_gro[data_message[0]]:
                    sock_cl.send(json.dumps(str(data_message[1]), ensure_ascii=False).encode("utf-8"))
            else:
                sock_cli.send(json.dumps("Вы ввели цифру меньше 100", ensure_ascii=False).encode("utf-8"))
        else:
            sock_cli.send(
                json.dumps(f"Сообщение испорчено, попробуйте отослать ещё раз! ", ensure_ascii=False).encode("utf-8"))

    @staticmethod
    def ser_add_g(sock_cli, base_gro):
        """Создание или добавление группы"""
        sock_cli.send(json.dumps(str(f"Список групп: {base_gro}"), ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
        if data_message in base_gro:
            for k, v in base_gro.items():
                if k == data_message:
                    if sock_cli in v:
                        sock_cli.send(
                            json.dumps("Вы уже создали или добавились в группу", ensure_ascii=False).encode("utf-8"))
                        break
                    elif sock_cli not in v:
                        v.append(sock_cli)
                        base_gro.update({data_message: v})
                        sock_cli.send(json.dumps("Вы успешно добавились в группу", ensure_ascii=False).encode("utf-8"))
                        break
        elif str(data_message.strip("#")).isdigit():
            if int(data_message.strip("#")) >= 100:
                base_gro.update({data_message: [sock_cli]})
                sock_cli.send(json.dumps("Вы успешно создали группу", ensure_ascii=False).encode("utf-8"))
            else:
                sock_cli.send(json.dumps("Вы ввели цифру меньше 100", ensure_ascii=False).encode("utf-8"))
        else:
            sock_cli.send(json.dumps(f"Запрос на создание или удаление не удался, попробуйте ещё раз! ",
                                     ensure_ascii=False).encode("utf-8"))

    @staticmethod
    def ser_run(sock_cli, base_cli, base_gro, func_p, func_g, func_add, func_base):
        """Запуск внутреннего сценария сервера"""
        while True:
            base_all_client = {f'#{z}': base_cli[z] for z in range(len(base_cli))}
            try:
                data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
            except Exception as ex:
                log_send(ex)
                break
            if data_message == "П":
                p_send_p = Thread(target=func_p, args=(sock_cli, base_all_client, func_base))
                p_send_p.daemon = True
                p_send_p.start()
            elif data_message == "Г":
                p_send_g = Thread(target=func_g, args=(sock_cli, base_gro))
                p_send_g.daemon = True
                p_send_g.start()
            elif data_message == "ВГ":
                p_add_g = Thread(target=func_add, args=(sock_cli, base_gro))
                p_add_g.daemon = True
                p_add_g.start()

    def server_original(self):
        """Запуск сервера"""
        clients = []
        base_group = {}

        while True:
            try:
                cli, adr = self.sock.accept()
            except OSError:
                print("Help")
            else:
                id_auth = self.auth_server(cli)
                self.history_client(cli, id_auth)
                print(f"Получен запрос на соединение от {adr}")
                clients.append(cli)
            finally:
                wait = 10
                w = []
                try:
                    r, w, er = select.select([], clients, [], wait)
                except Exception as err:
                    print(f"Клиент отключился{err}")

                for s in w:
                    t_st = Thread(target=self.ser_run,
                                  args=(
                                      s, w, base_group, self.ser_send_p, self.ser_send_g, self.ser_add_g,
                                      self.add_contacts))
                    t_st.daemon = True
                    t_st.start()


def start_parser(ip="127.0.0.1", tcp=7777):
    """Сценарий для терминала"""
    parser = argparse.ArgumentParser(description='Запуск сервера')
    parser.add_argument("-a", type=str, help='Выбор ip')
    parser.add_argument("-p", type=int, help='Выбор tcp')
    args = parser.parse_args()
    if args.a and args.p is not None:
        a = Server(args.a, args.p)
        a.server_original()
    elif args.a or args.p is None:
        a = Server(ip, tcp)
        a.server_original()
    elif args.a is None:
        a = Server(ip, args.p)
        a.server_original()
    elif args.p is None:
        a = Server(args.a, tcp)
        a.server_original()


if __name__ == '__main__':
    start_parser()
