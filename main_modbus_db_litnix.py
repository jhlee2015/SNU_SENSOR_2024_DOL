import logging
import threading
import time
#import serial
from datetime import datetime
import serial
import up_config_manager
import up_util
import up_logger_manager
import up_kongju_farm_databases as upDatabases
from pymodbus.client.serial import ModbusSerialClient as ModbusClient

# 로그 설정
# logging.basicConfig()
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)  # DEBUG 수준으로 설정하면 패킷 내용이 나옵니다

"""
센서 :litnix 암모니아, Co2, 온/습도 센서
인터페이스 : RS485 
저장방식: DB 직접 저장
"""

class LITNIX:

    def __init__(self):
        # serial_config = up_config_manager.ConfigManager().get_serial_config('AMA2')
        serial_config = up_config_manager.ConfigManager().get_serial_config('WINDOW')
        # tcp_modbus_config = up_config_manager.ConfigManager().get_modbus_server()
        sensor_id = up_config_manager.ConfigManager().get_sensor_id()
        print(serial_config)
        print(sensor_id)
        self.port = serial_config['port']
        self.baud = serial_config['baud']
        self.sensor_id = sensor_id['id']
        self.read_thread = None
        self.db = None
        self.slave_id = 1  # 슬레이브 ID
        self.address = 0  # 레지스터 시작 주소
        self.count = 10  # 읽을 레지스터 수
        self.client = ModbusClient(
            port=self.port,
            baudrate=int(self.baud),
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )

    def readthread(self):  # 데이터 받는 함수

        if self.client.connect():
            try:
                while True:
                    serial_logger.info("Sensor Pack Request!")
                    result = self.client.read_holding_registers(address=self.address, count=self.count,
                                                                   slave=self.slave_id)

                    if result.isError():
                        print("read fail:", result)

                    else:

                        #result = client.read_holding_registers(address=0, count=10, slave=1)  # unit=slave ID

                        # modbus 통신 테스트용
                        now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_date = datetime.now().strftime("%Y%m")

                        print(f"Holding Registers: {result.registers}")
                        temperature = result.registers[0] / 10.0  # ℃
                        humidity = result.registers[1] / 10.0  # %RH
                        ammonia = result.registers[2]  # ppm
                        co2 = result.registers[3]  # ppm
                        # 결과 출력
                        print(f"온도: {temperature:.1f} ℃")
                        print(f"습도: {humidity:.1f} %")
                        print(f"암모니아: {ammonia} ppm")
                        print(f"CO2: {co2} ppm")

                        # update 하기전에 컬럼이 존재 하는지 확인하기
                        #SV = upDatabases.SENSOR_VALUE(self.sensor_id, now_date, up_util.TEMP, temperature, log_date)
                        SV = upDatabases.SENSOR_VALUE(self.sensor_id, now_date, up_util.TEMP, temperature, log_date)
                        db_manager.updateSensor(SV)

                    # client.close()
                    time.sleep(5)
            except KeyboardInterrupt:
                serial_logger.info("중단됨 (Ctrl+C)")
            finally:
                self.client.close()
                serial_logger.info("Modbus 연결 종료됨.")
        else:
            self.client.close()
            serial_logger.info("Modbus connected fail")

if __name__ == '__main__':

    log_manager = up_logger_manager.LoggerManager()
    db_manager = upDatabases.DatabaseManager()
    util = up_util.UTIL()

    info_logger = log_manager.get_logger('info')
    serial_logger = log_manager.get_logger('serial')

    while True:
        serial_logger.info('Han Cnu Kisan flow Start')
        try:
            litnix = LITNIX()
            litnix.read_thread = threading.Thread(target=litnix.readthread)
            litnix.read_thread.daemon = True
            litnix.read_thread.start()
            while True:
                serial_logger.info("main Alive!! ")
                if litnix.read_thread is None or not litnix.read_thread.is_alive():
                    serial_logger.warning("thread dead! restarting...")
                    litnix = LITNIX()
                    litnix.read_thread.read_thread = threading.Thread(target=LITNIX.readthread, args=(litnix.client,))
                    litnix.read_thread.read_thread.daemon = True
                    litnix.read_thread.read_thread.start()
                    serial_logger.info("thread restarted.")
                time.sleep(60)

        except Exception as E:
            serial_logger.info('main error' + str(E))
            if litnix.client is not None:
                serial_logger.info('serial close ok')
                litnix.client.close()
            time.sleep(10)

