import os


def check_ip(str_ip):
    str_ip = str(str_ip)
    list_ip = []
    if str_ip.isdigit():
        return False
    else:
        str_ip = str_ip.split(".")
        for i in str_ip:
            if i.isdigit():
                list_ip.append(i.isdigit())
        if len(list_ip) == 4:
            return True
        return False


def check_tcp(str_tcp):
    str_tcp = str(str_tcp)
    if str_tcp.isdigit():
        if len(str_tcp) == 4:
            return True
        return False
    else:
        return False
