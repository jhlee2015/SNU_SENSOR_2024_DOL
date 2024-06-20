# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
import serial
from datetime import datetime
import up_util
import up_logger_manager
import up_databases
import up_config_manager

#DATA = "RM;202406201645;59500153;0;91;4;0.0;25.5;46.5;196;0;0;1;0;6.207;0D61"

class WD3000_DOMAIN:

    def __init__(self, create_dt=None, rain_during_interval=None, temp=None, rh=None, wind=None, maxwind=None, curwind=None, solar_radiation=None):
        self.create_dt = create_dt
        self.rain_during_interval = rain_during_interval
        self.temp = temp
        self.rh = rh
        self.wind = wind
        self.maxwind = maxwind
        self.curwind = curwind
        self.solar_radiation = solar_radiation


class WD3000:

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('WINDOW')
        sensor_id = up_config_manager.ConfigManager().get_sensor_id()
        print(serial_config)
        print(sensor_id)
        self.port = serial_config['port']
        self.baud = serial_config['baud']
        self.sensor_id = sensor_id['id']
        self.ser = None
        self.db = None

    def app_init(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=1)


    @staticmethod
    def wd3000_parser(DATA):
        try:
            serial_logger.info(DATA)
            # ;를 기준으로 문자열을 나눠줌
            parsing_data = DATA.split(';')


            if parsing_data[0] == 'RM':
                # 첵섬
                # if DATA[15] ==
                # datetimestr = datetime.datetime.now()
                # date = parsing_data[1]
                # datetimestr = "20{}-{}-{} {}:{}:{}".format(date[0:2], date[2:4], date[4:6], date[6:8], date[8:10],
                #                                           date[10:12])
                now = datetime.now()

                domain = WD3000_DOMAIN()
                domain.create_dt = now.strftime('%Y-%m-%d %H:%M:%S')

                domain.rain_during_interval = parsing_data[6]
                domain.temp = parsing_data[7]
                domain.rh = parsing_data[8]
                domain.wind = parsing_data[9]
                domain.maxwind = parsing_data[10]
                domain.curwind = parsing_data[11]
                domain.solar_radiation = parsing_data[12]
                Voltage = parsing_data[14]
                serial_logger.info('---' * 30)
                # print('Date: ' + datetimestr)
                serial_logger.info('Date:'+domain.create_dt+'SN:'+parsing_data[2]+', Signal Strenth: '+parsing_data[3])
                serial_logger.info('Battery Percent: ' + parsing_data[4]+', Configuration revision: ' + parsing_data[5])
                serial_logger.info('Rain during interval: ' + domain.rain_during_interval)
                serial_logger.info('Temparature: ' + domain.temp+', RH: ' + domain.rh+', wind: ' + domain.wind)
                serial_logger.info('maxwind: '+domain.maxwind+'curwind: ' + domain.curwind)
                serial_logger.info('solar_radiation: '+domain.solar_radiation+', Alerts: ' + parsing_data[13])
                serial_logger.info('Voltage at regulator input, solar panel output: ' + Voltage)
                serial_logger.info('CheckSum: ' + parsing_data[15])
                serial_logger.info("---" * 30)
                return domain
            else :
                print('else '+parsing_data[0])

        except Exception as E:
            print(str(E))
            serial_logger.debug("parsing error" + str(E))



    def main_loof(self):
        while True:
            if self.ser.readable():
                res = self.ser.readline()
                if res:
                    # print(res[0:3], type(res[0:3]))
                    domain = self.wd3000_parser(str(res.decode('utf-8')))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.RAIN_DURING_INTERVAL, domain.rain_during_interval))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.TEMP, domain.temp))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.HUM, domain.rh))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.WIND, domain.wind))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.MAX_WIND, domain.maxwind))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.CUR_WIND, domain.curwind))
                    db_manager.insert(query=db_manager.insertQuery,
                                      params=(datetime.now(), self.sensor_id, up_util.SOLAR_RADIATION, domain.solar_radiation))


if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = up_databases.DatabaseManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('SNU Pmc Control Start')
        try:
            pmc = WD3000()
            pmc.app_init()
            pmc.main_loof()

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if pmc.ser is not None:
                serial_logger.info('serial close ok')
                pmc.ser.close()
            time.sleep(10)
