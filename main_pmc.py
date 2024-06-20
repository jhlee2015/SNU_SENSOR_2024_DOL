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


class PMC:

    pmc_req = bytearray([0x01, 0x04, 0x00, 0x00, 0x00, 0x0e, 0x71, 0xCE])

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('AMA2')
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
    def readthread(ser):  # 데이터 받는 함수

        while True:
            serial_logger.info("Pmc Control Request")
            ser.write(PMC.pmc_req)
            time.sleep(6)

    @staticmethod
    def pmc_parser(DATA):
        try:
            ret = util.hextodec(DATA, "input")
            serial_logger.info(ret)

            #pmc
            temp = PMC.TEMP(DATA[3:5]) #온도
            vent1 = PMC.VENT(DATA[5:7]) #VENT1(%)
            vent2 = PMC.VENT(DATA[7:9]) #VENT2(%)
            vent3 = PMC.VENT(DATA[9:11]) #VENT3(%)
            pmc_error = PMC.ERROR(DATA[11:13])  # error
            serial_logger.info("temp val : " + temp)
            serial_logger.info("vent1 val : " + vent1+",vent1 val : " + vent2+",vent1 val : " + vent3)
            serial_logger.info("error val : " + pmc_error)
            return temp, vent1, vent2, vent3, pmc_error
        except Exception as E:
            serial_logger.debug("parsing error" + str(E))

    @staticmethod
    def TEMP(data):
        n = int(data.hex(), 16)
        n2 = float(n / 10)
        temp = "{0:.2f}".format(n2)
        return temp

    @staticmethod
    def VENT(data):
        n = int(data.hex(), 16)
        vent = "{0:.2f}".format(n)
        return vent

    @staticmethod
    def ERROR(data):
        n = int(data.hex(), 16)
        pmc_error = "{0:.2f}".format(n)
        return pmc_error

    def main_loof(self):
        while True:
            if self.ser.readable():
                res = self.ser.readline()
                if res:
                    if util.crc16(res) == [0, 0]:
                        util.hextodec(res, "response data : ")  # byte형식


                        # print(res[0:3], type(res[0:3]))
                        temp, vent1, vent2, vent3, error = self.pmc_parser(res)
                        db_manager.insert(query=db_manager.insertQuery,
                                          params=(datetime.now(), self.sensor_id, up_util.TEMP, temp))
                        db_manager.insert(query=db_manager.insertQuery,
                                          params=(datetime.now(), self.sensor_id, up_util.VENT1, vent1))
                        db_manager.insert(query=db_manager.insertQuery,
                                          params=(datetime.now(), self.sensor_id, up_util.VENT2, vent2))
                        db_manager.insert(query=db_manager.insertQuery,
                                          params=(datetime.now(), self.sensor_id, up_util.VENT3, vent3))

                    else:
                        serial_logger.info(datetime.datetime.now(), "CRC UNMATCHED DATA : ", res)


if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = up_databases.DatabaseManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('SNU Pmc Control Start')
        try:
            pmc = PMC()
            pmc.app_init()
            thread = threading.Thread(target=PMC.readthread, args=(pmc.ser,))  # 시리얼 통신 받는 부분
            thread.start()
            pmc.main_loof()

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if pmc.ser is not None:
                serial_logger.info('serial close ok')
                pmc.ser.close()
            time.sleep(10)
