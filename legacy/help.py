class ClientVerifier(type):

    def __new__(cls, *args, **kwargs):
        pass


class Client(metaclass=ClientVerifier):
    def __init__(self, ip, tcp):
        self.ip = ip
        self.tcp = tcp

    def __setattr__(self, name, value):
        # перегрузка методов
        self.__dict__[name] = value

    def new_socket(self):
        # Сокет в методе
        pass
