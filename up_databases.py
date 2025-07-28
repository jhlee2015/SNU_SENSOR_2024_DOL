# -*- coding: utf-8 -*-
import pymysql
import logging.config
import json
import time
from dateutil.parser import parse
import pymysql
import up_logger_manager
import up_config_manager
from up_util import UTIL

"""
DB 접속
DB 쿼리
"""

# mysql에 접속하고 disconnect되었을 때 재접하는 클레스
# 저장할 때 csv 형태로 같이 저장하게 한다.
class DatabaseManager:
    updateSensorQuery = 'update tb_sensor_value set timestamp=%s, sensing_value=%s  WHERE (device_id = %s and sensor_type = %s)'
    selectSensorQuery = 'select * from tb_sensor_value where device_id = %s and sensor_type = %s'
    insertSensorQuery = 'insert into tb_sensor_value(device_id, timestamp, sensor_type, sensing_value) values(%s, %s, %s, %s)'

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
        if self.conn_count == 10:
                self.disconnect()
                self.logger.info(f"Db Connection Fail 10 times Retry")
                self.conn_count = 0                    
                self.connect()
        try:
            if self.conn is not None:
                self.logger.info(f"Execute Success")
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params)
                self.conn.commit()
            else :
                self.logger.info(f"Execute Fail "+str(self.conn_count))
                self.conn_count += 1
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
            self.conn_count += 1
            self.logger.info(f"Error executing select: {e},conn_count:{self.conn_count}")
            if self.conn_count > 10:
                self.execute_query(query, params)
            # self.connect()
            # raise e

    def insert(self, query, params):
        try:
            csv_data = ','.join(str(param) for param in params)
            self.cvslogger.info(csv_data)
            self.execute_query(query, params)
            # self.logger.info(f"insert ok")
        except pymysql.MySQLError as e:
            self.conn_count += 1
            self.logger.info(f"Error executing insert: {e},conn_count:{self.conn_count}")
            if self.conn_count > 10:
                self.execute_query(query, params)
            # self.connect()
            # raise e

    def backUpinsert(self, query, params):
        try:
            self.execute_query(query, params)
            # self.logger.info(f"insert ok")
        except pymysql.MySQLError as e:
            self.conn_count += 1
            self.logger.info(f"Error executing insert: {e},conn_count:{self.conn_count}")
            if self.conn_count > 10:
                self.execute_query(query, params)
            # self.connect()
            # raise e

    def update(self, query, params):
        try:
            self.execute_query(query, params)
            # self.logger.info(f"update ok")
        except pymysql.MySQLError as e:
            self.conn_count += 1
            self.logger.info(f"Error executing update: {e},conn_count:{self.conn_count}")
            if self.conn_count > 10:
                self.execute_query(query, params)
            # self.connect()
            # raise e

    def updateSensor(self, SV):
        try:
            if self.select(query=self.selectSensorQuery, params=(SV.device_id, SV.sensor_type)):
                self.update(query=self.updateSensorQuery, params=(SV.timestamp, SV.sensing_value, SV.device_id, SV.sensor_type))
                self.logger.info(f"update ok")
            else:
                self.insert(query=self.insertSensorQuery, params=(SV.device_id, SV.timestamp, SV.sensor_type, SV.sensing_value))
                self.logger.info(f"insert ok")
            # 로그 저장
            make_log_query = self.get_insert_sensor_log_query('tb_sensing_value_'+SV.log_date)
            # print(make_log_query)
            self.insert(query=make_log_query, params=(SV.device_id, SV.timestamp, SV.sensor_type, SV.sensing_value))
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
    
    def check_table_exists(self, db_config, table_name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"SHOW TABLES LIKE '{table_name}';")
                result = cursor.fetchone()
                return result is not None
        except pymysql.MySQLError as e:
            self.logger.info(f"Error executing table check: {e}")
            # self.connect()
            # raise e

    def get_insert_sensor_log_query(self, table_name):
        return f'insert into {table_name}(device_id, timestamp, sensor_type, sensing_value) values(%s, %s, %s, %s)'


# device_id, timestamp, sensor_type, sensing_value을 포함한 객체 클레스
class SENSOR_VALUE:
    def __init__(self, device_id, timestamp, sensor_type, sensing_value, log_date):
        self.device_id = device_id
        self.timestamp = timestamp
        self.sensor_type = sensor_type
        self.sensing_value = sensing_value
        self.log_date = log_date

    def __str__(self):
        return f"device_id: {self.device_id}, timestamp: {self.timestamp}, sensor_type: {self.sensor_type}, sensing_value: {self.sensing_value}, log_date: {self.log_date}"

if __name__ == '__main__':
    log_manager = up_logger_manager.LoggerManager()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    dbManager = DatabaseManager()
    try:
        serial_logger.info('Databases Test Start')
        #dbManager.insert(query=DatabaseManager.insertQuery, params=(parse('2021-07-01 00:00:00'), '1', '1', '1'))
        sensor_list = dbManager.select(query='select * from tb_sensing_value_202501 where sensor_type = 1 and sensing_value > 1000')
        for sensor in sensor_list:
            print(sensor)
            if sensor[4] > 1000:
                sensor_value = sensor[4]*10
                # sensor_value 값을 2의 보수 적용하여 계산
                cal_val = UTIL.twos_complement(sensor_value, 16) / 10
                print(cal_val)
                #print(sensor[0])
        
                #time.sleep(2)    
                dbManager.update(query='UPDATE tb_sensing_value_202501 SET sensing_value = %s, timestamp = %s WHERE id = %s', params=(cal_val, sensor[2], sensor[0]))
                #time.sleep(1000)
            # dbManager.update(query='UPDATE tb_sensing_value_202412 SET sensing_value = %s WHERE id = %s', params=(1000, sensor[0]))
        time.sleep(10)
    except Exception as E:
        print(E)
    