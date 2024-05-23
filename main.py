# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
import serial
from datetime import datetime
import up_util as UP
import up_logger_manager
import up_databases

#PORT = 'COM11'
#-->raspi4 설정

PORT = '/dev/ttyAMA2'
#PORT = '/dev/ttyUSB3'
BAUD = 9600

kisan_req = bytearray([0x01, 0x04, 0x00, 0x82, 0x00, 0x08, 0x51, 0xE4])

class DOL:

    def __init__(self):
        self.ser = None
        self.db = None

    def app_init(self):
        self.ser = serial.Serial(PORT, BAUD, timeout=1)

    @staticmethod
    def readthread(ser):  # 데이터 받는 함수

        while True:
            serial_logger.info("Kisan Sensor Request")
            ser.write(kisan_req)
            time.sleep(5)

    @staticmethod
    def kisan_parser(DATA):
        try:
            ret = util.hextodec(DATA, "input")
            serial_logger.info(ret)

            # NH3
            nh3 = DOL.NH3(DATA[3:5])
            serial_logger.info("nh3 val : " + nh3)
            return nh3
        except Exception as E:
            serial_logger.debug("parsing error"+str(E))

    @staticmethod
    def NH3(data):
        n = int(data.hex(), 16)
        V = (n * 10) / 65535
        nh3 = "{0:.2f}".format(V * 10)
        return nh3

    def main_loof(self):
        while True:
            if self.ser.readable():
                res = self.ser.readline()
                if res:
                    if util.crc16(res) == [0, 0]:
                        util.hextodec(res, "response data : ")  # byte형식

                        # print(res[0:3], type(res[0:3]))
                        nh3 = self.kisan_parser(res)
                        db_manager.insert(query=db_manager.insertQuery, params=(datetime.now(), '1', '1', nh3))
                    else:
                        serial_logger.info(datetime.datetime.now(), "CRC UNMATCHED DATA : ", res)


if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = up_databases.DatabaseManager()
    util = UP.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('SNU Dol Sensor Start' )
        print('hahah')
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

