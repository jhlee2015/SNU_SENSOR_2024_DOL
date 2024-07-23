import pymysql
import logging.config
import json
import time
from dateutil.parser import parse
import pymysql
import up_logger_manager
import up_config_manager


# mysql에 접속하고 disconnect되었을 때 재접하는 클레스
# 저장할 때 csv 형태로 같이 저장하게 한다.
class DatabaseManager:
    insertQuery = 'insert into tb_sensing_value(create_dt, sensor_id, sensor_type, sensing_value) values(%s, %s, %s, %s)'

    insertKnuCowQuery = 'insert into tb_sensing_value(create_dt, sensor_id, sensor_type, wind_speed_value, wind_direction_value) values(%s, %s, %s, %s, %s)'

    def __init__(self):
        self.logger = up_logger_manager.LoggerManager().get_logger("db")
        self.cvslogger = up_logger_manager.LoggerManager().get_logger("csv")
        db_config = up_config_manager.ConfigManager().get_database_config()
        print(db_config)

        self.host = db_config['host']
        self.port = int(db_config['port'])
        self.user = db_config['user']
        self.password = db_config['password']
        self.db = db_config['database']
        self.charset = db_config['charset']
        self.conn = None
        self.conn_count = 0
        self.connect()

    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        password=self.password,
                                        db=self.db,
                                        charset=self.charset)
            self.logger.info(f"Connect !!")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error connecting to MySQL Platform: {e}")
            self.conn_count += 1
            # DB에 접속이 안되더라도 csv 파일로 저장해야되기 때문에 계속 접속하면 안됨
            # 10분 단위로 재접속을 시도하게 한다.
            
            # self.connect()
            # raise 사용하면 런타임 예외가 발생하여 중단된다.
            # raise e

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.logger.info(f"Disconnect !!")

    def execute_query(self, query, params=None):
        try:
            if self.conn is not None:
                self.logger.info(f"Execute Success")
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params)
                self.conn.commit()
            else :
                self.logger.info(f"Execute Fail "+str(self.conn_count))
                self.conn_count += 1
                if self.conn_count == 10:
                    self.logger.info(f"Db Connection Fail 10 times Retry")
                    self.conn_count = 0                    
                    self.connect()
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing query: {e}")
            self.conn_count += 1
            # self.connect()
            # raise e

    def select(self, query, params=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing select: {e}")
            # self.connect()
            # raise e

    def insert(self, query, params):
        try:
            csv_data = ','.join(str(param) for param in params)
            self.cvslogger.info(csv_data)
            self.execute_query(query, params)
            #self.logger.info(f"insert ok")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing insert: {e}")
            # self.connect()
            # raise e

    def update(self, query, params):
        try:
            self.execute_query(query, params)
            #self.logger.info(f"update ok")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing update: {e}")
            # self.connect()
            # raise e

    def delete(self, query, params):
        try:
            self.execute_query(query, params)
            #self.logger.info(f"delete ok")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing delete: {e}")
            # self.connect()
            # raise e


if __name__ == '__main__':
    log_manager = up_logger_manager.LoggerManager()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    dbManager = DatabaseManager()
    while True:
        try:
            serial_logger.info('Databases Test Start')
            dbManager.insert(query=DatabaseManager.insertQuery, params=(parse('2021-07-01 00:00:00'), '1', '1', '1'))
            time.sleep(10)
        except Exception as E:
            print(E)
            time.sleep(10)
