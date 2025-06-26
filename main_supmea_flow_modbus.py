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
from up_requests import apiRequestManager

# Float으로 변환
import struct

# import logging
#
# # pymodbus 로깅 레벨 설정
# logging.basicConfig()
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)  # or logging.INFO

class SUPMEA:

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('AMA2')
        sensor_id = up_config_manager.ConfigManager().get_sensor_id()
        print(serial_config)
        print(sensor_id)
        self.port = serial_config['port']
        self.baud = serial_config['baud']
        self.sensor_id = sensor_id['id']
        self.read_thread = None
        self.db = None
        self.apiManager = apiRequestManager()
        self.slave_id = 8  # 슬레이브 ID
        self.client = ModbusClient(
            port=self.port,
            baudrate=int(self.baud),
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )

    def readthread(self):  # 데이터 받는 함수

        serial_logger.info("Kisan Sensor Request1!")
        if self.client.connect():
            try:
                while True:

                    serial_logger.info("instantaneous flow")
                    read_result = self.client.read_input_registers(address=1000, count=2, slave=self.slave_id)

                    if read_result.isError():
                        print("read fail:", read_result)
                    else:
                        # Little Endian flow 계산하기
                        regs = read_result.registers
                        raw = struct.pack('<HH', regs[1], regs[0])
                        val = struct.unpack('<f', raw)[0]
                        print(f"instantaneous flow 값: {val}")

                    #client.close()

                    serial_logger.info("flow accumulation")
                    read_result = self.client.read_input_registers(address=1002, count=4, slave=self.slave_id)

                    if read_result.isError():
                        print("read fail:", read_result)
                    else:
                        # Little Endian flow 계산하기
                        regs = read_result.registers
                        data = struct.pack('<HHHH', regs[1], regs[0], regs[3], regs[2])

                        # 2. float64 (double)로 변환
                        value = struct.unpack('<d', data)[0]
                        print(f"flow double 값: {value}")

                    serial_logger.info("reverse flow accumulation")
                    read_result = self.client.read_input_registers(address=111, count=4, slave=self.slave_id)

                    if read_result.isError():
                        print("read fail:", read_result)
                    else:
                        # Little Endian flow 계산하기
                        regs = read_result.registers
                        int_raw = struct.pack('<HH', regs[1], regs[0])
                        int_val = struct.unpack('<f', int_raw)[0]
                        print(f"reverse flow 정수 값: {int_val}")

                        dec_raw = struct.pack('<HH', regs[3], regs[2])
                        dec_val = struct.unpack('<f', dec_raw)[0]
                        print(f"reverse flow 소수 값: {dec_val / 1000}")

                        print(f"reverse flow 최종 값: {int_val + (val / 1000)}")


                    time.sleep(5)
            except KeyboardInterrupt:
                print("중단됨 (Ctrl+C)")
            finally:
                self.client.close()
                print("Modbus 연결 종료됨.")
        else:
            self.client.close()
            print("Modbus connected fail")



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
