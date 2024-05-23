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

        self.makeHandler("info")
        self.makeHandler("serial")
        self.makeHandler("db")

    def makeHandler(self, name=None):
        logger = logging.getLogger(name)
        handler = logging.handlers.TimedRotatingFileHandler(filename="log/"+name+".log", when='midnight')
        handler.setFormatter(self.formatter)
        handler.suffix = "%Y-%m-%d"  # or anything else that strftime will allow

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(self.formatter)
        logger.addHandler(handler)
        logger.addHandler(console_handler)

    def get_logger(self, name=None):
        if name == "serial":
            return self.serial_logger
        return self.info_logger
