import time
import struct

from pymodbus.client import ModbusTcpClient


class modbus_tcp_client :

    # Modbus address to read
    @staticmethod
    def read_modbus_word(client, address, count):
        # Read holding registers (function code 3)
        response = client.read_holding_registers(address, count, unit=1)
        if response.isError():
            print(f"Error reading address {address}")
        else:
            # modbus 데이터 10개 출력
            for i in range(10):
                print(f"Value at address {address}: {response.registers[i]}")

    @staticmethod
    def write_modbus_word(client, address, value):
        # Holding Register에 단일 값 쓰기 (function code 6)
        response = client.write_register(address, value, unit=1)
        if response.isError():
            print(f"❌ Failed to write value at address {address}")
        else:
            print(f"✅ Wrote value {value} to address {address}")

    @staticmethod
    def write_modbus_float(client, address, float_value):
        # float → 4바이트 → 2개의 16비트 unsigned short로 변환
        float_bytes = struct.pack('>f', float_value)  # big-endian float
        high, low = struct.unpack('>HH', float_bytes)  # high = addr, low = addr+1

        # 두 개의 레지스터에 쓰기 (Function code 16 = write multiple registers)
        response = client.write_registers(address, [high, low], unit=1)

        if response.isError():
            print(f"❌ Failed to write float at address {address}")
        else:
            print(f"✅ Wrote float value {float_value} to address {address} ({[high, low]})")

    @staticmethod
    def read_modbus_float(client, address):
        # 2개의 연속된 Holding Register 읽기 (32비트 float)
        response = client.read_holding_registers(address=address, count=2, unit=1)

        if response.isError():
            print(f"❌ Failed to read float at address {address}")
            return None
        else:
            registers = response.registers
            high, low = registers[0], registers[1]
            print(f"📥 Raw registers: {registers}")

            # 레지스터 → float (big-endian 기준)
            float_bytes = struct.pack('>HH', high, low)
            float_value = struct.unpack('>f', float_bytes)[0]

            print(f"✅ Read float value {float_value} from address {address}")
            return float_value

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

        read_modbus_word(client, 0)

        # Close the connection
        client.close()
    else:
        print(f"Failed to connect to Modbus server at {SERVER_IP}")
