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

class LoggerManager:

    def __init__(self):
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)

        # self.info_log_init()
        self.serial_log_init()
        # self.db_log_init()

    def info_log_init(self):
        handler = logging.handlers.TimedRotatingFileHandler(filename="log/info.log", when='midnight')
        handler.setFormatter(self.formatter)
        handler.suffix = "%Y-%m-%d" # or anything else that strftime will allow

        self.info_logger = logging.getLogger("info")
        self.info_logger.setLevel(logging.INFO)
        self.info_logger.addHandler(handler)
        self.info_logger.addHandler(self.console_handler)

    def serial_log_init(self):
        handler = logging.handlers.TimedRotatingFileHandler(filename="log/serial.log", when='midnight')
        handler.setFormatter(self.formatter)
        handler.suffix = "%Y-%m-%d" # or anything else that strftime will allow

        self.serial_logger = logging.getLogger("serial")
        self.serial_logger.setLevel(logging.INFO)
        self.serial_logger.addHandler(handler)
        self.serial_logger.addHandler(self.console_handler)

    def db_log_init(self):
        handler = logging.handlers.TimedRotatingFileHandler(filename="log/db.log", when='midnight')
        handler.setFormatter(self.formatter)
        handler.suffix = "%Y-%m-%d" # or anything else that strftime will allow

        self.db_logger = logging.getLogger("db")
        self.db_logger.setLevel(logging.INFO)
        self.db_logger.addHandler(handler)
        self.db_logger.addHandler(self.console_handler)

    def get_logger(self, name=None):
        if name is 'serial':
            return self.serial_logger
        return self.info_logger



