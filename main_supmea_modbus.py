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
from pymodbus.client.serial import ModbusSerialClient as ModbusClient

# 한기술에서 사용하는 압력센서 supmea, SUP-PX400

class SUPMEA:

    #kisan_req = bytearray([0x01, 0x04, 0x00, 0x82, 0x00, 0x08, 0x51, 0xE4])

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
            baudrate=self.baud,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )


    @staticmethod
    def readthread(client):  # 데이터 받는 함수

        while True:
            if client.connect():
                slave_id = 1  # 슬레이브 ID
                address = 130  # 레지스터 시작 주소
                count = 8  # 읽을 레지스터 수
                serial_logger.info("Kisan Sensor Request!")
                read_result = client.read_input_registers(address=address, count=count, slave=slave_id)

                if read_result.isError():
                    print("read fail:", read_result)
                else:
                    values = read_result.registers
                    print(f"[read success] address {address}, Count{count} : {values}")
                    cal_val = (values[0] / 65535.0) * 20.0  # [0] 0채널
                    print(f"{cal_val:.3f} mA")

                client.close()
                time.sleep(1)
            else:
                print("Modbus connected fail")



    def main_loof(self):
        while True:
            if self.ser.readable():
                res = self.ser.readline()
                if res:
                    if util.crc16(res) == [0, 0]:
                        util.hextodec(res, "response data : ")  # byte형식

                        # print(res[0:3], type(res[0:3]))
                        nh3 = self.kisan_parser(res)
                        now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_date =datetime.now().strftime("%Y%m")
                        SV = up_databases.SENSOR_VALUE(self.sensor_id, now_date, up_util.NH3, nh3, log_date)
                        db_manager.updateSensor(SV)
                    else:
                        serial_logger.info(datetime.now(), "CRC UNMATCHED DATA : ", res)

if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = up_databases.DatabaseManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('SNU Dol Sensor Start')
        try:
            sup = SUPMEA()
            sup.app_init()
            thread = threading.Thread(target=SUPMEA.readthread, args=(sup.client,))  # 시리얼 통신 받는 부분
            thread.start()
            # sup.main_loof()

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if sup.client is not None:
                serial_logger.info('serial close ok')
                sup.client.close()
            time.sleep(10)
