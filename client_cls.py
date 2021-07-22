import argparse
import dis
import json
from socket import socket, AF_INET, SOCK_STREAM

from storage_sqlite import Storage, PATH
from service import log_send


class ClientVerifier(type):
    def __init__(cls, name_class, bases, dict_class):
        n = 0
        for key, value in dict_class.items():
            if isinstance(value, type(socket(AF_INET, SOCK_STREAM))):
                raise Exception("Должно отсутствовать создание сокетов на уровне класса")
            a = dis.code_info(value)
            if "accept" in a:
                raise Exception("Такой функции у сокета, как 'accept' не должна быть в классе")
            elif "listen" in a:
                raise Exception("Такой функции у сокета,как 'listen' не должна быть в классе")
            elif "SOCK_STREAM" in a:
                n = n + 1
        if n == 0:
            raise Exception(
                "Такая функция у сокета,как 'SOCK_STREAM' должна быть в классе, так как соединение должно быть TCP")
        type.__init__(cls, name_class, bases, dict_class)


class Client(metaclass=ClientVerifier):
    def __init__(self, ip="127.0.0.1", tcp=7778):
        self.ip = ip
        self.tcp = tcp
        self.sock = socket(AF_INET, SOCK_STREAM)

    def add_message(self, message):
        send_cli_s = self.sock.getsockname()
        base_data = Storage(PATH, "contacts")
        base_data.metadata.clear()
        result = base_data.get_contacts("SELECT * FROM histories_users")
        list_id_send = []
        for a in result:
            if str(a[3]) == str(send_cli_s):
                list_id_send.append(a[1])
        base_data = Storage(PATH, "history_message", login=list_id_send[0], message=str(message))
        base_data.add_base()

    def add_contact(self, cons):
        print(cons)
        send_cli_s = self.sock.getsockname()
        base_data = Storage(PATH, "contacts")
        base_data.metadata.clear()
        result = base_data.get_contacts("SELECT * FROM histories_users")
        list_id_send = []
        for a in result:
            if str(a[3]) == str(send_cli_s):
                list_id_send.append(a[1])
        base_data = Storage(PATH, "list_contacts", login=list_id_send[0], list_conta=str(cons))
        base_data.add_base()

    def auth_client(self):
        auth = input(
            'Введите, свой новый логин или используйте старый для входа в систему: '
        )
        self.sock.send(json.dumps(auth, ensure_ascii=False).encode("utf-8"))
        data_message = json.loads(self.sock.recv(1024).decode("utf-8"))
        if data_message is True:
            info = input(
                'Введите, информацию о себе: '
            )
            self.sock.send(json.dumps(info, ensure_ascii=False).encode("utf-8"))
        else:
            print(data_message)

    def cli_start(self):
        """Выбор сценария на сервере"""
        msg = input(
            'Введите, что вы хотите сделать (П/Отправить сообщение пользователю, '
            'Г/Отправить группе, ВГ/Вступить в группу, К/Посмотреть контакты)? '
        )
        self.sock.send(json.dumps(msg, ensure_ascii=False).encode("utf-8"))
        return msg

    def cli_rec(self):
        """Проверка сообщений от сервера"""
        self.sock.settimeout(1)
        try:
            data = self.sock.recv(1024).decode("utf-8")
        except Exception as ex:
            log_send(ex)
        else:
            data_message = json.loads(data)
            print(f"\nСообщение: {data_message}")
            log_send(data_message)
            return data_message

    def cli_send_p(self):
        """Отправка сообщений пользователям"""
        msg_a = input("Введите номер пользователя с #0 до #99 с которым хотите начать беседу: ")
        msg_b = input(f'Введите сообщение пользователю {msg_a}: ')
        self.add_message(str({msg_a: msg_b}))
        self.sock.send(json.dumps([msg_a, msg_b], ensure_ascii=False).encode("utf-8"))

    def cli_send_g(self):
        """Отправка сообщений группе"""
        msg_a = input("Введите номер группы с #100 до #999 с которым хотите начать беседу: ")
        msg_b = input(f'Введите сообщение группе {msg_a}: ')
        self.sock.send(json.dumps([msg_a, msg_b], ensure_ascii=False).encode("utf-8"))

    def cli_add_g(self):
        """Создание или добавление группы"""
        msg_a = input("Введите номер группы от #100 которую хотите создать или подключится: ")
        self.sock.send(json.dumps(msg_a, ensure_ascii=False).encode("utf-8"))

    def client_original(self):
        """Запуск клиента"""
        with self.sock as s:
            s.connect((self.ip, self.tcp))
            self.auth_client()
            while True:
                self.cli_rec()
                msg_1 = self.cli_start()
                if msg_1 == 'П':
                    self.cli_rec()
                    self.cli_send_p()
                    self.cli_rec()
                elif msg_1 == 'Г':
                    self.cli_rec()
                    self.cli_send_g()
                    self.cli_rec()
                elif msg_1 == 'ВГ':
                    self.cli_rec()
                    self.cli_add_g()
                    self.cli_rec()
                elif msg_1 == 'К':
                    con = self.cli_rec()
                    self.add_contact(con)
                else:
                    pass


def start_client_parser(ip="127.0.0.1", tcp=7777):
    """Сценарий для терминала"""
    parser = argparse.ArgumentParser(description='Запуск клиента')
    parser.add_argument("a", type=str, help='Выбор ip', nargs='?')
    parser.add_argument("p", type=int, help='Выбор tcp', nargs='?')
    args = parser.parse_args()
    if args.a and args.p is not None:
        a = Client(args.a, args.p)
        a.client_original()
    else:
        a = Client(ip, tcp)
        a.client_original()


if __name__ == '__main__':
    start_client_parser()
