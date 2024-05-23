# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
import serial
from datetime import datetime
import up_util as UP
import up_logger_manager
import up_databases

PORT = 'COM11'
#-->raspi4 설정
#PORT = '/dev/ttyS0'
#PORT = '/dev/ttyUSB3'
BAUD = 9600

soha_req = bytearray([0x01, 0x03, 0x00, 0x64, 0x00, 0x03, 0x44, 0x14])

class DOL:

    def __init__(self):
        self.ser = None
        self.db = None

    def app_init(self):

        self.ser = serial.Serial(PORT, BAUD, timeout=1)

    @staticmethod
    def readthread(ser):  # 데이터 받는 함수

        while True:
            serial_logger.info("Soha Sensor Request")
            ser.write(soha_req)
            time.sleep(5)

    @staticmethod
    def soha_parser(data):
        co2_value = data[3:5]
        temp_value = data[5:7]
        rh_value = data[7:9]

        print("*" * 30)
        print("Device ID :", data[0])

        print("*" * 30)

        print("Co2 value :", int(co2_value.hex(), 16))
        true_co2_value = int(co2_value.hex(), 16)

        #id, type, value
        db_manager.insert(query=db_manager.insertQuery, params=(datetime.now(), '1', util.CO2, true_co2_value))

        print("temp value :", int(temp_value.hex(), 16))
        true_temp_value = int(temp_value.hex(), 16) / 10
        db_manager.insert(query=db_manager.insertQuery, params=(datetime.now(), '1', util.TEMP, true_temp_value))

        print('RH value : ', int(rh_value.hex(), 16))
        true_rh_value = int(rh_value.hex(), 16) / 10
        db_manager.insert(query=db_manager.insertQuery, params=(datetime.now(), '1', util.HUM, true_rh_value))

        print("-" * 40)
        print('dev_id : ', data[0])
        print("real_co2 value :", int(co2_value.hex(), 16), 'ppm')
        print('real_temp_value : ', true_temp_value, 'ºC')
        print('real_rh_value : ', true_rh_value, "%")
        print("-" * 40)



    def main_loof(self):
        while True:
            if self.ser.readable():
                # print('start')
                res = self.ser.readline()
                if res:
                    if util.crc16(res) == [0, 0]:
                        ret = util.hextodec(res, "inpu : ")  # byte형식
                        serial_logger.info(ret)
                        # print(res[0:3], type(res[0:3]))
                        self.soha_parser(res)

                    else:
                        serial_logger.info(datetime.datetime.now(), "CRC UNMATCHED DATA : ", res)


if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = up_databases.DatabaseManager()
    util = UP.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        try:
            dol = DOL()
            dol.app_init()
            thread = threading.Thread(target=DOL.readthread, args=(dol.ser,))  # 시리얼 통신 받는 부분
            thread.start()
            dol.main_loof()

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if dol.ser is not None:
                serial_logger.info('serial close ok')
                dol.ser.close()
            time.sleep(10)

