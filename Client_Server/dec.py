from log.server_log_config import logger


def logs(function_ser_cli):
    """
    Передает имя и аргументы декорируемой функции
    """

    def calling(*args, **kwargs):
        logger.info(f'Сообщение: Имя функции {function_ser_cli.__name__} и аргументы функции {args}')
        return function_ser_cli(*args, **kwargs)

    calling.__name__ = function_ser_cli.__name__
    return calling


if __name__ == "__main__":
    pass
