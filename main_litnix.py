from pymodbus.client import ModbusSerialClient as ModbusClient
import logging

# 로그 설정
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)  # DEBUG 수준으로 설정하면 패킷 내용이 나옵니다

# Configure Modbus RTU client
client = ModbusClient(
    method='rtu',
    port='COM7',  # Or COM3 on Windows
    baudrate=9600,
    stopbits=1,
    bytesize=8,
    parity='N',
    timeout=1
)

# Connect to the Modbus slave
connection = client.connect()
print(f"Connected: {connection}")

if connection:
    # Read 2 holding registers starting from address 0
    result = client.read_holding_registers(address=0, count=10,  slave=1)  # unit=slave ID

    if not result.isError():
        print(f"Holding Registers: {result.registers}")
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
    else:
        print(f"Error: {result}")

    # Close connection
    client.close()
else:
    print("Failed to connect to Modbus device.")
