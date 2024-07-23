# -*- coding: utf-8 -*-
import threading
import time
import serial
from datetime import datetime

import up_config_manager
import up_util
import up_logger_manager
import up_databases

# Carbonized Wind Speed Direction Sensor

class CWSDS:

    # 한개의 라즈베리파이가 최대 8개의 풍향풍속계를 관장하게 된다.
    cwsds_req_1 = bytearray([0x25, 0x03, 0x00, 0x00, 0x00, 0x04, 0x42, 0xed])
    cwsds_req_2 = bytearray([0x26, 0x03, 0x00, 0x00, 0x00, 0x04, 0x42, 0xde])
    cwsds_req_3 = bytearray([0x27, 0x03, 0x00, 0x00, 0x00, 0x04, 0x43, 0x0f])
    cwsds_req_4 = bytearray([0x28, 0x03, 0x00, 0x00, 0x00, 0x04, 0x43, 0xf0])
    cwsds_req_5 = bytearray([0x29, 0x03, 0x00, 0x00, 0x00, 0x04, 0x42, 0x21])
    cwsds_req_6 = bytearray([0x30, 0x03, 0x00, 0x00, 0x00, 0x04, 0x40, 0x28])

    def __init__(self):
        serial_config = up_config_manager.ConfigManager().get_serial_config('WINDOW')
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
            serial_logger.info("Cwsds Sensor Request")
            ser.write(CWSDS.cwsds_req_1)
            time.sleep(5)

    @staticmethod
    def cwsds_parser(data, sensor_id):
        wind_id = data[0:1]
        wind_speed_value = data[3:5]
        wind_level_value = data[5:7]
        wind_direction_value = data[7:9]

        true_wind_id = int(wind_id.hex(), 16)
        true_wind_speed_value = int(wind_speed_value.hex(), 16) /10
        true_wind_level_value = int(wind_level_value.hex(), 16)
        true_wind_direction_value = int(wind_direction_value.hex(), 16) / 10

        db_manager.insert(query=db_manager.insertKnuCowQuery,
                  params=(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), true_wind_id, up_util.WIND_SPEED_DIRECTION,
                      true_wind_speed_value, true_wind_direction_value))

        serial_logger.info('sensor id :'+str(true_wind_id))
        serial_logger.info('real wind speed value : '+str(true_wind_speed_value)+'m/s')
        serial_logger.info('real wind level value : '+str(true_wind_level_value)+' levle')
        serial_logger.info('real wind direction value : '+str(true_wind_direction_value)+' angle')


    def main_loof(self):
        while True:
            if self.ser.readable():
                # print('start')
                res = self.ser.readline()
                if res:
                    if util.crc16(res) == [0, 0]:
                        ret = util.hextodec(res, "input : ")  # byte형식
                        serial_logger.info(ret)
                        # print(res[0:3], type(res[0:3]))
                        self.cwsds_parser(res, self.sensor_id)

                    else:
                        serial_logger.info(datetime.now(), "CRC UNMATCHED DATA : ", res)


if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = up_databases.DatabaseManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        try:
            cwsds = CWSDS()
            cwsds.app_init()
            thread = threading.Thread(target=CWSDS.readthread, args=(cwsds.ser,))  # 시리얼 통신 받는 부분
            thread.start()
            cwsds.main_loof()

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if cwsds.ser is not None:
                serial_logger.info('serial close ok')
                cwsds.ser.close()
            time.sleep(10)
