# 1. Для всех функций из урока 3 написать тесты
# с использованием unittest. Они должны быть оформлены
# в отдельных скриптах
# с префиксом test_ в имени файла (например, test_client.py).
# * Использовал pytest
from check import check_tcp, check_ip
from server import server_connect

tcp_one = 7777
ip_one = "127.0.0.1"


def test_server_tcp():
    assert check_tcp(tcp_one) is True, "Неправильный прописан tcp"
    server_connect(tcp_start=tcp_one)


def test_server_ip():
    assert check_ip(ip_one) is True, "Неправильный прописан ip"
    server_connect(ip_one, tcp_one)
