import configparser
import up_util
import os


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class ConfigManager:

    def __init__(self):
        util = up_util.UTIL()
        # 로그 저장할 폴더 생성
        current_dir = '{}'.format(util.get_current_dir())

        self.config = configparser.ConfigParser()

        print(current_dir + '/config.ini')
        self.config.read(current_dir + '/config.ini',encoding='utf-8')

    def get_os_config(self):
        os_config = {
            'os_name': self.config.get('OS', 'OS_NAME')
        }
        return os_config

    def get_database_config(self):
        db_config = {
            'host': self.config.get('database', 'HOST'),
            'port': self.config.get('database', 'PORT'),
            'user': self.config.get('database', 'USER'),
            'password': self.config.get('database', 'PASSWORD'),
            'database': self.config.get('database', 'DATABASE'),
            'charset': self.config.get('database', 'CHARSET')
        }
        return db_config

    def get_serial_config(self, name=None):
        serial_config = {}
        if name == 'S0':
            serial_config = {
                'port': self.config.get('serial_s0', 'PORT'),
                'baud': self.config.get('serial_s0', 'BAUD')
            }
        elif name == 'AMA0':
            serial_config = {
                'port': self.config.get('serial_ama0', 'PORT'),
                'baud': self.config.get('serial_ama0', 'BAUD')
            }
        elif name == 'AMA1':
            serial_config = {
                'port': self.config.get('serial_ama1', 'PORT'),
                'baud': self.config.get('serial_ama1', 'BAUD')
            }
        elif name == 'AMA2':
            serial_config = {
                'port': self.config.get('serial_ama2', 'PORT'),
                'baud': self.config.get('serial_ama2', 'BAUD')
            }
        elif name == "WINDOW":
            serial_config = {
                'port': self.config.get('serial_window', 'PORT'),
                'baud': self.config.get('serial_window', 'BAUD')
            }
        return serial_config

    def get_settings(self):
        settings = {
            'debug': self.config.getboolean('settings', 'debug'),
            'log_file': self.config.get('settings', 'log_file')
        }
        return settings

    def get_sensor_id(self):
        sensor_id = {
            'id': self.config.get('sensor_id', 'ID')
        }
        return sensor_id
