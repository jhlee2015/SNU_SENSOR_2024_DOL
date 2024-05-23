import logging
import logging.handlers
import os

# 현재 파일 경로 및 파일명 찾기
current_dir = os.path.dirname(os.path.realpath(__file__))
current_file = os.path.basename(__file__)
current_file_name = current_file[:-3]  # xxxx.py
LOG_FILENAME = 'log-{}'.format(current_file_name)

# 로그 저장할 폴더 생성
log_dir = '{}/log'.format(current_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class LoggerManager:

    def __init__(self):
        self.info_logger = self.makeHandler("info")
        self.serial_logger = self.makeHandler("serial")
        self.db_logger = self.makeHandler("db")

    @staticmethod
    def makeHandler(name=None):
        handler = logging.handlers.TimedRotatingFileHandler(filename="log/" + name + ".log", when='midnight')
        handler.setFormatter(FORMATTER)
        handler.setLevel(logging.INFO)
        handler.suffix = "%Y-%m-%d"  # or anything else that strftime will allow

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(FORMATTER)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.addHandler(console_handler)

        return logger

    @staticmethod
    def get_logger(name=None):
        if name:
            return logging.getLogger(name)
        return logging.getLogger("info")

