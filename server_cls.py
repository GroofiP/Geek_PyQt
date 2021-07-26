import argparse
import dis
import json
import select

from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from sqlalchemy.exc import IntegrityError

from storage_sqlite import Storage, PATH, User, Contacts
from service import log_send


class PortVerifier:
    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError(f"Значение должно быть типа {int}")
        instance.__dict__[self.tcp] = value

    def __set_name__(self, owner, name):
        self.tcp = name


class ServerVerifier(type):

    def __init__(cls, name_class, bases, dict_class):
        n = 0
        for key, value in dict_class.items():
            if key != "tcp":
                a = dis.code_info(value)
                if "connect" in a:
                    raise Exception("Такого метода как 'connect' не должно быть в классе")
                elif "SOCK_STREAM" in a:
                    n = n + 1
        if n == 0:
            raise Exception(
                "Такая функция у сокета,как 'SOCK_STREAM' должна быть в классе, так как соединение должно быть TCP")
        type.__init__(cls, name_class, bases, dict_class)


class Server(metaclass=ServerVerifier):
    tcp = PortVerifier()

    def __init__(self, ip, tcp):
        self.ip = ip
        self.tcp = tcp
        self.sock = self.server_con()
        self.base_group = {}
        self.client_all = {}
        self.id_user = {}

    def forms_client(self, base_cli):
        list_v = []
        for v in self.id_user.keys():
            list_v.append(v)
        base_all_client = {list_v[-1]: base_cli[-1]}
        return base_all_client

    def base_auth_server(self, sock_cli):
        auth = json.loads(sock_cli.recv(1024).decode("utf-8"))
        base_data = Storage(PATH, "users")
        base_data.con_base()
        session = base_data.session_con()
        user = session.query(User).filter_by(login=auth).first()
        if user is None:
            sock_cli.sendall(json.dumps(True, ensure_ascii=False).encode("utf-8"))
            info = json.loads(sock_cli.recv(1024).decode("utf-8"))
            base_data = Storage(PATH, "users", {"login": auth, "information": info})
            base_data.add_base()
            base_data.metadata.clear()
        else:
            sock_cli.sendall(json.dumps("Вы авторизованы", ensure_ascii=False).encode("utf-8"))
        user = session.query(User).filter_by(login=auth).first()
        self.base_history_client(sock_cli, user.id)
        return {user.login: user.id}

    @staticmethod
    def base_history_client(sock_cli, id_user):
        time = datetime.today().strftime("%Y.%m.%d %H:%M:%S")
        ip_date = sock_cli.getpeername()
        base_data = Storage(PATH, "histories_users",
                            {"id_user": int(id_user), "date": str(time), "ip_date": str(ip_date)})
        base_data.metadata.clear()
        base_data.add_base()

    def base_add_contacts(self, sock_cli_send, sock_cli_recv):
        send_cli_s = sock_cli_send
        send_cli_r = sock_cli_recv
        base_data = Storage(PATH, "contacts")
        base_data.metadata.clear()
        id_send, id_recv = [], []
        for key, value in self.client_all.items():
            if str(value) == str(send_cli_s) and str(value) == str(send_cli_r):
                id_send = self.id_user[key]
                id_recv = self.id_user[key]
            elif str(value) == str(send_cli_s):
                id_send = self.id_user[key]
            elif str(value) == str(send_cli_r):
                id_recv = self.id_user[key]
        base_data = Storage(PATH, "contacts", {"id_send": int(id_send), "id_recv": int(id_recv)})
        base_data.add_base()

    def base_contacts(self, sock_cli):
        id_name = ""
        for k, v in self.client_all.items():
            if v == sock_cli:
                id_name = self.id_user[k]
        base_data = Storage(PATH, "contacts")
        base_data.con_base()
        session = base_data.session_con()
        users_contacts = session.query(Contacts).filter_by(id_send=id_name)
        name = []
        for item in users_contacts:
            user_name = session.query(User).filter_by(id=item.id_recv).first()
            name.append(user_name.login)
        return name

    def server_con(self):
        """Развертывание сервера на определенном ip и tcp"""
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.ip, self.tcp))
        sock.listen(5)
        return sock

    def ser_send_p(self, sock_cli):
        """Отправка сообщений пользователям"""
        sock_cli.sendall(json.dumps(str(f"Список клиентов: {self.client_all}"), ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
        dict_message = {}
        for k, v in self.client_all.items():
            if sock_cli == v:
                dict_message = {k: data_message[1]}
        try:
            self.client_all[data_message[0]].sendall(
                json.dumps(dict_message, ensure_ascii=False).encode("utf-8"))
        except Exception as ex:
            sock_cli.sendall(
                json.dumps(f"Сообщение испорчено, попробуйте отослать ещё раз! ", ensure_ascii=False).encode("utf-8"))
            log_send(ex)
        try:
            self.base_add_contacts(sock_cli, self.client_all[data_message[0]])
        except IntegrityError:
            print("Уже добавлен в контакты")

    def ser_send_g(self, sock_cli):
        """Отправка сообщений группе"""
        sock_cli.sendall(json.dumps(str(f"Список групп: {self.base_group}"), ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
        if str(data_message[0].strip("#")).isdigit():
            if int(data_message[0].strip("#")) >= 100:
                for sock_cl in self.base_group[data_message[0]]:
                    sock_cl.sendall(json.dumps(str(data_message[1]), ensure_ascii=False).encode("utf-8"))
            else:
                sock_cli.sendall(json.dumps("Вы ввели цифру меньше 100", ensure_ascii=False).encode("utf-8"))
        else:
            sock_cli.sendall(
                json.dumps(f"Сообщение испорчено, попробуйте отослать ещё раз! ", ensure_ascii=False).encode("utf-8"))

    def ser_add_g(self, sock_cli):
        """Создание или добавление группы"""
        sock_cli.sendall(json.dumps(str(f"Список групп: {self.base_group}"), ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
        if data_message in self.base_group:
            for k, v in self.base_group.items():
                if k == data_message:
                    if sock_cli in v:
                        sock_cli.sendall(
                            json.dumps("Вы уже создали или добавились в группу", ensure_ascii=False).encode("utf-8"))
                        break
                    elif sock_cli not in v:
                        v.append(sock_cli)
                        self.base_group.update({data_message: v})
                        sock_cli.sendall(
                            json.dumps("Вы успешно добавились в группу", ensure_ascii=False).encode("utf-8"))
                        break
        elif str(data_message.strip("#")).isdigit():
            if int(data_message.strip("#")) >= 100:
                self.base_group.update({data_message: [sock_cli]})
                sock_cli.sendall(json.dumps("Вы успешно создали группу", ensure_ascii=False).encode("utf-8"))
            else:
                sock_cli.sendall(json.dumps("Вы ввели цифру меньше 100", ensure_ascii=False).encode("utf-8"))
        else:
            sock_cli.sendall(json.dumps(f"Запрос на создание или удаление не удался, попробуйте ещё раз! ",
                                        ensure_ascii=False).encode("utf-8"))

    def ser_run(self, sock_cli):
        """Запуск внутреннего сценария сервера"""
        while True:
            data_message = json.loads(sock_cli.recv(1024).decode("utf-8"))
            if data_message == "П":
                self.ser_send_p(sock_cli)
            elif data_message == "Г":
                self.ser_send_g(sock_cli)
            elif data_message == "ВГ":
                self.ser_add_g(sock_cli)
            elif data_message == "К":
                dict_contacts = self.base_contacts(sock_cli)
                sock_cli.sendall(json.dumps(dict_contacts, ensure_ascii=False).encode("utf-8"))

    def server_original(self):
        """Запуск сервера"""
        clients = []

        while True:
            try:
                cli, adr = self.sock.accept()
            except OSError:
                print("Help")
            else:
                self.id_user.update(self.base_auth_server(cli))
                print(f"Получен запрос на соединение от {adr}")
                clients.append(cli)
            finally:
                wait = 10
                w = []
                try:
                    r, w, er = select.select([], clients, [], wait)
                except Exception as err:
                    print(f"Клиент отключился{err}")

                self.client_all.update(self.forms_client(w))

                for s in w:
                    t_st = Thread(target=self.ser_run, args=(s,))
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
