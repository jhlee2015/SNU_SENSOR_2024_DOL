# -*- coding: utf-8 -*-
import threading
from _thread import *
import time
from datetime import datetime
import up_util
import up_logger_manager
import up_config_manager
import up_modbus_tcp_client as mclient
from pymodbus.client.serial import ModbusSerialClient as ModbusClient
from pymodbus.client import ModbusTcpClient

# 한기술에서 사용하는 압력센서 supmea, SUP-PX400
from up_requests import apiRequestManager


class SUPMEA:

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('AMA2')
        tcp_modbus_config = up_config_manager.ConfigManager().get_modbus_server('modbus_server')
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
        self.client = ModbusClient(
            port=self.port,
            baudrate=int(self.baud),
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        self.tcp_client = ModbusTcpClient(self.modbus_host, port=self.modbus_port)

    def readthread(self):  # 데이터 받는 함수

        if self.client.connect():
            try:
                while True:
                    serial_logger.info("Kisan Sensor Request!")
                    read_result = self.client.read_input_registers(address=self.address, count=self.count, slave=self.slave_id)

                    if read_result.isError():
                        print("read fail:", read_result)
                    else:
                        values = read_result.registers
                        print(f"[read success] address {self.address}, Count{self.count} : {values}")
                        cal_val = (values[0] / 65535.0) * 20.0  # [0] 0채널
                        print(f"{cal_val:.3f} mA")
                        cal_val_bar = up_util.UTIL.current_to_bar(cal_val)

                        #res = self.apiManager.send_sensor_data("irrigation_sensor", "s001", "press", cal_val_bar)
                        mclient.modbus_tcp_client.write_modbus_float(self.tcp_client, 1, cal_val_bar)

                    #client.close()
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
