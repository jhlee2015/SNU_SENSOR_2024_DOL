# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
from datetime import datetime
import up_util
import up_logger_manager
import up_config_manager
from pymodbus.client.serial import ModbusSerialClient as ModbusClient
import minimalmodbus

# 한기술에서 사용하는 압력센서 supmea, SUP-PX400
from up_requests import apiRequestManager
import serial


class SUPMEA:

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('AMA4')
        sensor_id = up_config_manager.ConfigManager().get_sensor_id()
        print(serial_config)
        print(sensor_id)
        self.port = serial_config['port']
        self.baud = serial_config['baud']
        self.sensor_id = sensor_id['id']
        self.read_thread = None
        self.db = None
        self.apiManager = apiRequestManager()
        self.slave_id = 1  # 슬레이브 ID
        self.address = 130  # 레지스터 시작 주소
        self.count = 8  # 읽을 레지스터 수
        self.client = None

    def readthread(self):  # 데이터 받는 함수
        serial_logger.info("Kisan out ")
        self.__init__()
        self.client = minimalmodbus.Instrument(self.port, slaveaddress=1, mode='rtu')
        self.client.serial.baudrate = int(self.baud)
        self.client.serial.bytesize = 8
        self.client.serial.parity = serial.PARITY_NONE
        self.client.serial.stopbits = 1
        self.client.serial.timeout = 1
        value = 4000  # 20.000 mA
        try:
            while True:
                # A 채널 (레지스터 0x0002) → 20,000 (20.000mA)
                reg_addr = 0x0002
                self.client.write_register(reg_addr, value, functioncode=16)
                print("A 채널에 20mA 설정 완료")

                time.sleep(7)
                value = value - 2000  # 20.000 mA
                print(value)
        finally:
            print("Modbus 연결 에러")

if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('Han Cnu Kisan Start')
        try:
            sup = SUPMEA()
            sup.read_thread = threading.Thread(target=sup.readthread)
            sup.read_thread.daemon = True
            sup.read_thread.start()
            while True:
                serial_logger.info("main Alive!! ")
                if sup.read_thread is None or not sup.read_thread.is_alive():
                    serial_logger.warning("thread dead! restarting...")
                    sup.read_thread.read_thread = threading.Thread(target=SUPMEA.readthread, args=(sup.client,))
                    sup.read_thread.read_thread.daemon = True
                    sup.read_thread.read_thread.start()
                    serial_logger.info("thread restarted.")
                time.sleep(6)

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if sup.client is not None:
                serial_logger.info('serial close ok')
                sup.client.close()
            time.sleep(10)
