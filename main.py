import ipaddress
import subprocess

from tabulate import tabulate

ip_address_all = [
    "coderoad.ru",
    "techrocks.ru",
    "gb.ru",
    "192.168.31.24",
    "127.0.0.1"
]


def host_ping(list_ip):
    """
    Функция, проверяющая доступность сетевых узлов

        Параметры:
            list_ip (list): список с ip и/или хост адресами.
        Возвращаемое значение:
            None: Функция ничего не возвращает
    """
    for ip in list_ip:
        if "".join(ip.split(".")).isdigit():
            ip = ipaddress.ip_address(ip)
        sub_ping = subprocess.Popen(["ping", "-c", "3", str(ip)], stdout=subprocess.PIPE)
        result = sub_ping.stdout.read()
        if "Unreachable" in result.decode():
            print(f"Узел недоступен: {ip}")
        else:
            print(f"Узел доступен: {ip}")


def host_range_ping(ip_start_dia):
    """
    Функция, проверяющая доступность сетевых узлов и отображающия их в виде сколько доступно,
    а сколько нет

        Параметры:
            ip_start_dia (str): ip address по которому будет идти итерация в диапозоне его последнего октета.
        Возвращаемое значение:
            None: Функция ничего не возвращает
    """
    subnet = ipaddress.ip_network(ip_start_dia)
    r = 0
    u = 0
    for ip in subnet:
        sub_ping = subprocess.Popen(["ping", "-c", "1", str(ip)], stdout=subprocess.PIPE)
        result = sub_ping.stdout.read()
        if "Unreachable" in result.decode():
            u += 1
        else:
            r += 1
    print(f"Доступных узлов: {r}\n"
          f"Недоступных узлов: {u}")


def host_range_ping_tab(ip_start_dia):
    """
    Функция, проверяющая доступность сетевых узлов и отображающия их в виде колонок,
    где написано, какие доступны, а какие нет.

        Параметры:
            ip_start_dia (str): ip address по которому будет идти итерация в диапозоне его последнего октета.
        Возвращаемое значение:
            None: Функция ничего не возвращает
    """
    subnet = ipaddress.ip_network(ip_start_dia)
    answer = {
        "Unreachable": [],
        "Reachable": []
    }
    for ip in subnet:
        sub_ping = subprocess.Popen(["ping", "-c", "1", str(ip)], stdout=subprocess.PIPE)
        result = sub_ping.stdout.read()
        if "Unreachable" in result.decode():
            answer["Unreachable"].append(ip)
        else:
            answer["Reachable"].append(ip)
    print(tabulate(answer, headers="keys"))


if __name__ == "__main__":
    host_range_ping_tab("192.168.31.0/28")
