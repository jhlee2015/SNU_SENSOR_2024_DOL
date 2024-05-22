# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
import serial
from datetime import datetime
import up_util as UP
import up_logger_manager

#PORT = 'COM11'
#-->raspi4 설정
PORT = '/dev/ttyAMA1'
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
            now = datetime.datetime.now()
            cutime = now.strftime('%Y-%m-%d %H:%M:%S')

            # if DATA[19:21] ==
            util.hextodec(DATA, "input")

            print("length : ", hex(DATA[2]))
            print("-" * 30)


            # NH3
            nh3 = DOL.NH3(DATA[3:5])
            print("NH3 value : ", nh3)

            # nh3_value = domain.SENSOR_STATUS(cutime, 2, nh3, '1')
            # database.DATABASE.insert(nh3_value)
            # ONEM2M.ONEM2M.request_post(2, 0, nh3)
            # print("CH3 : ", DATA[7:9])


            serial_logger.info("nh3 val : " + nh3 )

            # print("CH6 : ", DATA[13:15])
            # print("CH7 : ", DATA[15:17])
            # print("CH8 : ", DATA[17:19])
        except Exception as E:
            print("parsing error")
            print(E)
            serial_logger.info(E)

    @staticmethod
    def NH3(data):
        n = int(data.hex(), 16)
        V = (n * 10) / 65535
        hum = "{0:.2f}".format(V * 10)

        return hum

    def main_loof(self):
        while True:
            if self.ser.readable():
                # print('start')
                res = self.ser.readline()
                if res:
                    if util.crc16(res) == [0, 0]:
                        util.hextodec(res, "responsedata : ")  # byte형식

                        # print(res[0:3], type(res[0:3]))
                        self.kisan_parser(res)
                    else:
                        serial_logger.info(datetime.datetime.now(), "CRC UNMATCHED DATA : ", res)


if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
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

