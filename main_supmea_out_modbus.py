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
from pymodbus.client import ModbusTcpClient
import up_modbus_tcp_client as mclient
# 한기술에서 사용하는 압력센서 supmea, SUP-PX400
from up_requests import apiRequestManager
import serial

"""
센서 : 벨브센서(출력)
인터페이스 : kisan 장비
저장 : modbus 저장
"""

class SUPMEA:

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('AMA4')
        #serial_config = up_config_manager.ConfigManager().get_serial_config('WINDOW')
        tcp_modbus_config = up_config_manager.ConfigManager().get_modbus_server()
        sensor_id = up_config_manager.ConfigManager().get_sensor_id()
        print(serial_config)
        print(sensor_id)
        self.port = serial_config['port']
        self.baud = serial_config['baud']
        self.modbus_host = tcp_modbus_config['host']
        self.modbus_port = tcp_modbus_config['port']
        self.sensor_id = sensor_id['id']
        self.read_thread = None
        self.db = None
        self.apiManager = apiRequestManager()
        self.slave_id = 1  # 슬레이브 ID
        self.address = 130  # 레지스터 시작 주소
        self.count = 8  # 읽을 레지스터 수
        self.client = None
        self.tcp_client = ModbusTcpClient(self.modbus_host, port=self.modbus_port)

    def readthread(self):  # 데이터 받는 함수
        serial_logger.info("Kisan out ")
        self.client = minimalmodbus.Instrument(self.port, slaveaddress=1, mode='rtu')
        self.client.serial.baudrate = int(self.baud)
        self.client.serial.bytesize = 8
        self.client.serial.parity = serial.PARITY_NONE
        self.client.serial.stopbits = 1
        self.client.serial.timeout = 1
        #value = 8000  # 20.000 mA
        try:
            while True:
                # 28 A, 30 B, 32 C, 34 D 채널
                read_value = mclient.modbus_tcp_client.read_modbus_float(serial_logger, self.tcp_client, 28)
                serial_logger.info("read "+str(read_value))
                # A 채널 (레지스터 0x0002) → 20,000 (20.000mA)
                self.client.write_register(0x0002, read_value, functioncode=16)
                serial_logger.info("A 채널 설정 완료")
                time.sleep(2)

                read_value = mclient.modbus_tcp_client.read_modbus_float(serial_logger, self.tcp_client, 30)
                serial_logger.info("read " + str(read_value))
                # B 채널 (레지스터 0x0003) → 20,000 (20.000mA)
                self.client.write_register(0x0003, read_value, functioncode=16)
                serial_logger.info("B 채널 설정 완료")
                time.sleep(2)

                read_value = mclient.modbus_tcp_client.read_modbus_float(serial_logger, self.tcp_client, 32)
                serial_logger.info("read " + str(read_value))
                # C 채널 (레지스터 0x0004) → 20,000 (20.000mA)
                self.client.write_register(0x0004, read_value, functioncode=16)
                time.sleep(2)
                serial_logger.info("C 채널 설정 완료")

                read_value = mclient.modbus_tcp_client.read_modbus_float(serial_logger, self.tcp_client, 34)
                serial_logger.info("read " + str(read_value))
                # D 채널 (레지스터 0x0005) → 20,000 (20.000mA)
                self.client.write_register(0x0005, read_value, functioncode=16)
                serial_logger.info("D 채널 설정 완료")

                time.sleep(20)
        finally:
            serial_logger.info("Modbus 연결 에러")

if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('Han Cnu Kisan Out Start')
        try:
            sup = SUPMEA()
            sup.read_thread = threading.Thread(target=sup.readthread)
            sup.read_thread.daemon = True
            sup.read_thread.start()
            while True:
                serial_logger.info("main Alive!! ")
                if sup.read_thread is None or not sup.read_thread.is_alive():
                    serial_logger.warning("thread dead! restarting...")
                    sup = SUPMEA()
                    sup.read_thread.read_thread = threading.Thread(target=SUPMEA.readthread, args=(sup.client,))
                    sup.read_thread.read_thread.daemon = True
                    sup.read_thread.read_thread.start()
                    serial_logger.info("thread restarted.")
                time.sleep(60)

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if sup.client is not None:
                serial_logger.info('serial close ok')
                sup.client.close()
            time.sleep(10)
