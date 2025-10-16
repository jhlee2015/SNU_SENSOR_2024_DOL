import time
import struct

from pymodbus.client import ModbusTcpClient

"""
modbus client에서 사용하는 워드, float, double 메소드
"""

class modbus_tcp_client :

    # Modbus address to read
    @staticmethod
    def read_modbus_16bit(log, client, address):
        # 1개의 Holding Register 읽기 (16비트)
        response = client.read_holding_registers(address=address, count=1, unit=1)

        if response.isError():
            log.info(f"Failed to read 16-bit value at address {address}")
            return None
        else:
            register = response.registers[0]
            log.info(f"Raw register: {register}")

            # 레지스터 → 16비트 unsigned int (big-endian 기준)
            reg_bytes = struct.pack('>H', register)
            value = struct.unpack('>H', reg_bytes)[0]  # Unsigned 16-bit int

            log.info(f"Read 16-bit value {value} from address {address}")
            return value

    @staticmethod
    def write_modbus_16bit(log, client, address, value):
        # 16비트 값 → 2바이트 (unsigned short, Big-endian)
        value_bytes = struct.pack('>H', value)
        register_value = struct.unpack('>H', value_bytes)[0]

        # 1개의 레지스터에 값 쓰기
        response = client.write_register(address=address, value=register_value, unit=1)

        if response.isError():
            log.info(f"Failed to write 16-bit value {value} to address {address}")
            return False
        else:
            log.info(f"Wrote 16-bit value {value} to address {address}")
            return True

    @staticmethod
    def read_modbus_word(log, client, address):
        # 2개의 연속된 Holding Register 읽기 (32비트 정수)
        response = client.read_holding_registers(address=address, count=2, unit=1)

        if response.isError():
            log.info(f"Failed to read word (32-bit int) at address {address}")
            return None
        else:
            registers = response.registers
            high, low = registers[0], registers[1]
            log.info(f"Raw registers: {registers}")

            # 레지스터 → 32비트 int (big-endian 기준)
            word_bytes = struct.pack('>HH', high, low)
            word_value = struct.unpack('>I', word_bytes)[0]  # Unsigned 32-bit int

            log.info(f"Read 32-bit word value {word_value} from address {address}")
            return word_value

    @staticmethod
    def write_modbus_word(log, client, address, value):
        # Holding Register에 단일 값 쓰기 (function code 6)
        response = client.write_register(address, value, unit=1)
        if response.isError():
            log.info(f"Failed to write value at address {address}")
        else:
            log.info(f"Wrote value {value} to address {address}")

    @staticmethod
    def write_modbus_float(log, client, address, float_value):
        # float → 4바이트 → 2개의 16비트 unsigned short로 변환
        float_bytes = struct.pack('>f', float_value)  # big-endian float
        high, low = struct.unpack('>HH', float_bytes)  # high = addr, low = addr+1

        # 두 개의 레지스터에 쓰기 (Function code 16 = write multiple registers)
        response = client.write_registers(address, [high, low], unit=1)

        if response.isError():
            log.info(f"Failed to write float at address {address}")
        else:
            log.info(f"Wrote float value {float_value} to address {address} ({[high, low]})")

    @staticmethod
    def read_modbus_float(log, client, address):
        # 2개의 연속된 Holding Register 읽기 (32비트 float)
        response = client.read_holding_registers(address=address, count=2, unit=1)

        if response.isError():
            log.info(f"Failed to read float at address {address}")
            return None
        else:
            registers = response.registers
            high, low = registers[0], registers[1]
            log.info(f"Raw registers: {registers}")

            # 레지스터 → float (big-endian 기준)
            float_bytes = struct.pack('>HH', high, low)
            float_value = round(struct.unpack('>f', float_bytes)[0],2)

            log.info(f"Read float value {float_value} from address {address}")
            return float_value

    import struct
    @staticmethod
    def read_modbus_double(log, client, address):
        # 4개의 연속된 Holding Register 읽기 (64비트 double)
        response = client.read_holding_registers(address=address, count=4, unit=1)

        if response.isError():
            log.info(f"Failed to read double at address {address}")
            return None
        else:
            registers = response.registers
            log.info(f"Raw registers: {registers}")

            if len(registers) != 4:
                log.info(f"Expected 4 registers but got {len(registers)}")
                return None

            h1, h2, l1, l2 = registers  # big-endian 순서

            # 레지스터 4개 → double (big-endian 기준)
            double_bytes = struct.pack('>HHHH', h1, h2, l1, l2)
            double_value = round(struct.unpack('>d', double_bytes)[0], 4)

            log.info(f"Read double value {double_value} from address {address}")
            return double_value


    @staticmethod
    def write_modbus_double(log, client, address, double_value):
        # double 값을 8바이트 → 4개의 16비트 레지스터 (big-endian)
        double_bytes = struct.pack('>d', double_value)
        registers = struct.unpack('>HHHH', double_bytes)
        h1, h2, l1, l2 = registers  # big-endian 순서

        # 4개의 연속된 Holding Register에 쓰기
        response = client.write_registers(address=address, values=[h1, h2, l1, l2], unit=1)

        if response.isError():
            log.info(f"Failed to write double value {double_value} to address {address}")
            return False
        else:
            log.info(f"Wrote double value {double_value} to address {address} ({[h1, h2, l1, l2]})")
            return True


if __name__ == '__main__':
    # Create Modbus TCP client
    SERVER_IP = "112.220.65.42"
    SERVER_PORT = 5020
    client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

    # Connect to the server
    if client.connect():
        print(f"Connected to Modbus server at {SERVER_IP}")

        # Read value from the specified address
        # read_modbus_word(client, ADDRESS)

        # write_modbus_word(client, address=0, value=12345)

        # time.sleep(1)

        # read_modbus_word(client, 0)

        # Close the connection
        client.close()
    else:
        print(f"Failed to connect to Modbus server at {SERVER_IP}")
