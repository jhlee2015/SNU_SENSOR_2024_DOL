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
    else:
        print(f"Error: {result}")

    # Close connection
    client.close()
else:
    print("Failed to connect to Modbus device.")
