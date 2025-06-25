# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
from datetime import datetime
import up_util
import up_logger_manager
import up_config_manager
from pymodbus.client.serial import ModbusSerialClient as ModbusClient

# 한기술에서 사용하는 압력센서 supmea, SUP-PX400

class SUPMEA:

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('TTY0')
        sensor_id = up_config_manager.ConfigManager().get_sensor_id()
        print(serial_config)
        print(sensor_id)
        self.port = serial_config['port']
        self.baud = serial_config['baud']
        self.sensor_id = sensor_id['id']
        self.client = None
        self.db = None

    def app_init(self):
        self.client = ModbusClient(
            port=self.port,
            baudrate=int(self.baud),
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )

    @staticmethod
    def readthread(client):  # 데이터 받는 함수
        slave_id = 1  # 슬레이브 ID
        address = 130  # 레지스터 시작 주소
        count = 8  # 읽을 레지스터 수
        serial_logger.info("Kisan Sensor Request1!")
        if client.connect():
            try:
                while True:

                    serial_logger.info("Kisan Sensor Request2!")
                    read_result = client.read_input_registers(address=address, count=count, slave=slave_id)

                    if read_result.isError():
                        print("read fail:", read_result)
                    else:
                        values = read_result.registers
                        print(f"[read success] address {address}, Count{count} : {values}")
                        cal_val = (values[0] / 65535.0) * 20.0  # [0] 0채널
                        print(f"{cal_val:.3f} mA")

                    #client.close()
                    time.sleep(5)
            except KeyboardInterrupt:
                print("중단됨 (Ctrl+C)")
            finally:
                client.close()
                print("Modbus 연결 종료됨.")
        else:
            client.close()
            print("Modbus connected fail")

    def main_loof(self):
        while True:
            serial_logger.info(datetime.now(), "main Alive!! ")
            time.sleep(600)

if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('Han Cnu Kisan Start')
        try:
            sup = SUPMEA()
            sup.app_init()
            thread = threading.Thread(target=SUPMEA.readthread, args=(sup.client,))  # 시리얼 통신 받는 부분
            thread.start()
            sup.main_loof()

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if sup.client is not None:
                serial_logger.info('serial close ok')
                sup.client.close()
            time.sleep(10)
