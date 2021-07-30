import argparse
import dis
import json
from socket import socket, AF_INET, SOCK_STREAM

from storage_sqlite import Storage, PATH, History
from service import log_send, login_required


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
                n += 1
        if n == 0:
            raise Exception(
                "Такая функция у сокета,как 'SOCK_STREAM' должна быть в классе, так как соединение должно быть TCP")
        type.__init__(cls, name_class, bases, dict_class)


class Client(metaclass=ClientVerifier):
    def __init__(self, ip="127.0.0.1", tcp=7778, res_queue=None):
        self.ip = ip
        self.tcp = tcp
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.res_queue = res_queue

    def add_message(self, message):
        send_cli_s = self.sock.getsockname()
        base_data = Storage(PATH, "histories_users")
        base_data.con_base()
        session = base_data.session_con()
        user_history = session.query(History).filter_by(ip_date=str(send_cli_s)).first()
        id_user = user_history.id_user
        base_data = Storage(PATH, "history_message", {"id_send": int(id_user), "message": message})
        base_data.add_base()

    def add_contact(self, cons):
        send_cli_s = self.sock.getsockname()
        base_data = Storage(PATH, "histories_users")
        base_data.con_base()
        session = base_data.session_con()
        user_history = session.query(History).filter_by(ip_date=str(send_cli_s)).first()
        id_user = user_history.id_user
        base_data = Storage(PATH, "list_contacts", {"id_send": int(id_user), "list_con": cons})
        base_data.add_base()

    def validate_get(self, text):
        if self.res_queue is None:
            item = input(text)
        else:
            print(text)
            item = self.res_queue.get()
        return item

    def auth_client(self):
        while True:
            auth_text = 'Введите, свой новый логин или используйте старый для входа в систему: '
            password_text = 'Введите пароль: '
            info_text = 'Введите, информацию о себе: '
            auth = self.validate_get(auth_text)
            self.sock.send(json.dumps(auth, ensure_ascii=False).encode("utf-8"))
            password = self.validate_get(password_text)
            self.sock.send(json.dumps(password, ensure_ascii=False).encode("utf-8"))
            data_message = json.loads(self.sock.recv(1024).decode("utf-8"))
            if data_message is True:
                info = self.validate_get(info_text)
                self.sock.send(json.dumps(info, ensure_ascii=False).encode("utf-8"))
            data_message = json.loads(self.sock.recv(1024).decode("utf-8"))
            if data_message == "Вы авторизованы":
                print(data_message)
                return auth
            else:
                print(data_message)

    def cli_start(self):
        """Выбор сценария на сервере"""
        msg_text = 'Введите, что вы хотите сделать (П/Отправить сообщение пользователю,Г/Отправить группе, ' \
                   'ВГ/Вступить в группу)? '
        msg = self.validate_get(msg_text)
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
        msg_a_text = "Введите ник пользователя с которым хотите начать беседу: "
        msg_b_text = f'Введите сообщение пользователю: '
        msg_a = self.validate_get(msg_a_text)
        msg_b = self.validate_get(msg_b_text)
        self.add_message(str({msg_a: msg_b}))
        self.sock.send(json.dumps([msg_a, msg_b], ensure_ascii=False).encode("utf-8"))

    def cli_send_g(self):
        """Отправка сообщений группе"""
        msg_a_text = "Введите номер группы с #100 до #999 с которым хотите начать беседу: "
        msg_b_text = f'Введите сообщение группе: '
        msg_a = self.validate_get(msg_a_text)
        msg_b = self.validate_get(msg_b_text)
        self.sock.send(json.dumps([msg_a, msg_b], ensure_ascii=False).encode("utf-8"))

    def cli_add_g(self):
        """Создание или добавление группы"""
        msg_a_text = "Введите номер группы от #100 которую хотите создать или подключится: "
        msg_a = self.validate_get(msg_a_text)
        self.sock.send(json.dumps(msg_a, ensure_ascii=False).encode("utf-8"))

    @login_required
    def cli_a(self, auth=None):
        list_local_user = json.loads(self.sock.recv(1024).decode("utf-8"))
        if auth == "Доступно только Groofi":
            self.res_queue.put("Нету доступа")
        elif self.res_queue is None:
            print(list_local_user)
        elif auth is not None:
            self.res_queue.put(list_local_user)

    def client_original(self):
        """Запуск клиента"""
        with self.sock as s:
            s.connect((self.ip, self.tcp))
            auth = self.auth_client()
            while True:
                self.cli_rec()
                try:
                    msg_1 = self.cli_start()
                except KeyboardInterrupt:
                    print("\nДо свидания!")
                    msg_1 = "ВЫХОД"
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
                    con = json.loads(self.sock.recv(1024).decode("utf-8"))
                    if self.res_queue is None:
                        print(con)
                    else:
                        self.res_queue.put(con)
                    self.add_contact(con)
                elif msg_1 == 'ВЫХОД':
                    return
                elif msg_1 == "А":
                    self.cli_a(auth)
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
