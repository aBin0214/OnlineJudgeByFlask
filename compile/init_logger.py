import logging.handlers


def init_logger(name):
    logger = logging.getLogger(name)

    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename="log/sys.log")

    logger.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.WARNING)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("(%(asctime)s)--%(name)s--%(levelname)s:%(message)s")
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

