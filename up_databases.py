import pymysql
import logging.config
import json
import time
from dateutil.parser import parse
import pymysql
import up_logger_manager

DB_HOST = '221.158.214.211'
DB_PORT = 14444
DB_USER = 'aquaGuest'
DB_PASSWORD = 'Dkzndk34&*'
DB_DATABASE = 'snu'
DB_CHARSET = 'utf8'


#mysql에 접속하고 disconnect되었을 때 재접하는 클레스
class DatabaseManager:

    insertQuery = 'insert into tb_sensing_value(create_dt, sensor_id, sensor_type, sensing_value) values(%s, %s, %s, %s)'

    def __init__(self):
        self.host = DB_HOST
        self.port = DB_PORT
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.db = DB_DATABASE
        self.charset = DB_CHARSET
        self.conn = None
        self.connect()
        self.logger = up_logger_manager.LoggerManager().get_logger("db")

    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        password=self.password,
                                        db=self.db,
                                        charset=self.charset)
        except pymysql.MySQLError as e:
            self.logger.info(f"Error connecting to MySQL Platform: {e}")
            raise e

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing query: {e}")
            raise e

    def select(self, query, params=None):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing select: {e}")
            raise e

    def insert(self, query, params):
        try:
            self.execute_query(query, params)
            self.logger.info(f"insert ok")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing insert: {e}")
            raise e

    def update(self, query, params):
        try:
            self.execute_query(query, params)
            self.logger.info(f"update ok")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing update: {e}")
            raise e

    def delete(self, query, params):
        try:
            self.execute_query(query, params)
            self.logger.info(f"delete ok")
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing delete: {e}")
            raise e           

if __name__ == '__main__':
    dbManager = DatabaseManager()

    while True:
        try:
            print("start")
            dbManager.insert(query = insertQuery, params = (parse('2021-07-01 00:00:00'), '1', '1', '1'))
            time.sleep(10)
        except Exception as E:
            print(E)
            time.sleep(10)