import argparse
import dis
import json
import time
from socket import socket, AF_INET, SOCK_STREAM

from service import log_send


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        for key, value in clsdict.items():
            if isinstance(value, type(socket(AF_INET, SOCK_STREAM))):
                raise Exception("Должно отсутствовать создание сокетов на уровне класса")
            a = dis.code_info(value)
            if "accept" in a:
                raise Exception("Такой функции у сокета, как 'accept' не должна быть в классе")
            elif "listen" in a:
                raise Exception("Такой функции у сокета,как 'listen' не должна быть в классе")
            elif key == "__init__":
                if "SOCK_STREAM" not in a:
                    raise Exception(
                        "Такая функция у сокета,как 'SOCK_STREAM' должна быть в классе, так как соединение должно быть TCP")
        type.__init__(self, clsname, bases, clsdict)


class Client(metaclass=ClientVerifier):
    def __init__(self, ip="127.0.0.1", tcp=7778):
        self.ip = ip
        self.tcp = tcp
        self.sock = socket(AF_INET, SOCK_STREAM)

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
            'Г/Отправить группе, ВГ/Вступить в группу)? '
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

    def cli_send_p(self):
        """Отправка сообщений пользователям"""
        msg_a = input("Введите номер пользователя с #0 до #99 с которым хотите начать беседу: ")
        msg_b = input(f'Введите сообщение пользователю {msg_a}: ')
        time.sleep(5)
        self.sock.send(json.dumps([msg_a, msg_b], ensure_ascii=False).encode("utf-8"))

    def cli_send_g(self):
        """Отправка сообщений группе"""
        msg_a = input("Введите номер группы с #100 до #999 с которым хотите начать беседу: ")
        msg_b = input(f'Введите сообщение группе {msg_a}: ')
        time.sleep(5)
        self.sock.send(json.dumps([msg_a, msg_b], ensure_ascii=False).encode("utf-8"))

    def cli_add_g(self):
        """Создание или добавление группы"""
        msg_a = input("Введите номер группы от #100 которую хотите создать или подключится: ")
        time.sleep(5)
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
