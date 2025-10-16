import pymysql
import logging.config
import json
import time
from dateutil.parser import parse

DB_HOST = '112.220.65.42'
DB_PORT = 12787
DB_USER = 'uptension'
DB_PASSWORD = 'password12#'
DB_DATABASE = 'cnu_no6'
DB_CHARSET = 'utf8'


class DATABASE:
    with open('logging.json', 'rt') as f:
        config = json.load(f)

    logging.config.dictConfig(config)

    logger = logging.getLogger('database')

    def insertWCvalue(self, value):
        try:
            conn = pymysql.connect(host=DB_HOST,
                                   port=DB_PORT,
                                   user=DB_USER,
                                   password=DB_PASSWORD,
                                   db=DB_DATABASE,
                                   charset=DB_CHARSET)
            try:
                with conn.cursor() as curs:
                    dt = parse(value.create_dt)
                    sql = 'insert into watertbl_boksim(name, recv_time, state_1, state_2, state_3, batt, temp)' \
                          ' values(%s, %s, %s, %s, %s, %s, %s)'
                    curs.execute(sql, (
                        value.name, value.create_dt, value.state_1, value.state_2, value.state_3,
                        value.batt, value.temp))
                conn.commit()
                DATABASE.logger.info('db insert ok ')
            finally:
                conn.close()
        except Exception as E:
            print(E)
            DATABASE.logger.info('db connect error')

    @staticmethod
    def updateWCvalue(state, time, name):
        try:
            conn = pymysql.connect(host=DB_HOST,
                                   port=DB_PORT,
                                   user=DB_USER,
                                   password=DB_PASSWORD,
                                   db=DB_DATABASE,
                                   charset=DB_CHARSET)
            try:
                with conn.cursor() as curs:
                    sql = 'update water_control_boksim set state_1=%s, recv_time=%s where name=%s'
                    curs.execute(sql, (state, time, name))
                conn.commit()
                DATABASE.logger.info('db update ok ')
            finally:
                conn.close()
        except Exception as E:
            print(E)
            DATABASE.logger.info('db connect error')


    @staticmethod
    def selectWaterControlState(value):
        try:
            conn = pymysql.connect(host=DB_HOST,
                                   port=DB_PORT,
                                   user=DB_USER,
                                   password=DB_PASSWORD,
                                   db=DB_DATABASE,
                                   charset=DB_CHARSET)
            try:
                with conn.cursor() as curs:
                    sql = 'select * from water_control_boksim where %s'
                    curs.execute(sql, value)
                    result = curs.fetchall()
                    print('Select OK')

                    return result
                conn.commit()

                DATABASE.logger.info('db Select ok ')
            finally:
                conn.close()
        except Exception as E:
            print(E)
            DATABASE.logger.info('db connect error')

    @staticmethod
    def selectWaterControlLast(value):
        try:
            conn = pymysql.connect(host=DB_HOST,
                                   port=DB_PORT,
                                   user=DB_USER,
                                   password=DB_PASSWORD,
                                   db=DB_DATABASE,
                                   charset=DB_CHARSET)
            try:
                with conn.cursor() as curs:
                    sql = 'select * from watertbl_boksim where name=%s order by recv_time desc limit 1'
                    curs.execute(sql, value)
                    result = curs.fetchall()
                    print('Select selectWaterControlLast OK')
                    print(result)
                    return result
                conn.commit()

                DATABASE.logger.info('db Select ok ')
            finally:
                conn.close()
        except Exception as E:
            print(E)
            DATABASE.logger.info('db connect error')

    @staticmethod
    def selectWaterControlStateAll():
        try:
            conn = pymysql.connect(host=DB_HOST,
                                   port=DB_PORT,
                                   user=DB_USER,
                                   password=DB_PASSWORD,
                                   db=DB_DATABASE,
                                   charset=DB_CHARSET)
            try:
                print('Select OK1')
                with conn.cursor() as curs:
                    sql = 'select * from water_control_boksim'
                    curs.execute(sql)
                    result = curs.fetchall()
                    print('Select OK2')

                    return result
                conn.commit()

                DATABASE.logger.info('db Select ok ')
            finally:
                conn.close()
        except Exception as E:
            print(E)
            DATABASE.logger.info('db connect error')

if __name__ == '__main__':
    #db = DATABASE()
    while True:
        try:
            print("start")
            DATABASE.selectWaterControlStateAll()
            #time.sleep(10)
        except Exception as E:
            print(E)
            time.sleep(10)