from bluepy import btle
import struct
import time

class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.temperature1 = None
        self.humidity1 = None
        self.temperature2 = None
        self.humidity2 = None

    def handleNotification(self, cHandle, data):
        try:
            if cHandle == self.temp_handle1:
                self.temperature1 = struct.unpack('f', data)[0]
                print(f"Received temperature1: {self.temperature1}")
            elif cHandle == self.humid_handle1:
                self.humidity1 = struct.unpack('f', data)[0]
                print(f"Received humidity1: {self.humidity1}")
            elif cHandle == self.temp_handle2:
                self.temperature2 = struct.unpack('f', data)[0]
                print(f"Received temperature2: {self.temperature2}")
            elif cHandle == self.humid_handle2:
                self.humidity2 = struct.unpack('f', data)[0]
                print(f"Received humidity2: {self.humidity2}")
        except Exception as e:
            print(f"Error handling notification: {e}")

    def to_dict(self):
        return {
            'temperature1': self.temperature1,
            'humidity1': self.humidity1,
            'temperature2': self.temperature2,
            'humidity2': self.humidity2
        }

def connect_to_peripheral(target_address):
    print(f"Connecting to {target_address}...")
    while True:
        try:
            peripheral = btle.Peripheral(target_address)
            delegate = NotificationDelegate()
            peripheral.setDelegate(delegate)
            return peripheral, delegate
        except btle.BTLEDisconnectError as e:
            print(f"Failed to connect to peripheral: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(2)

def enable_notifications(peripheral, characteristic_uuid):
    characteristic = peripheral.getCharacteristics(uuid=characteristic_uuid)[0]
    setup_data = b"\x01\x00"
    peripheral.writeCharacteristic(characteristic.getHandle() + 1, setup_data, withResponse=True)
    return characteristic.getHandle()

def receive_data(peripheral, delegate):
    try:
        print("Connected. Waiting for notifications...")

        # Enable notifications for the characteristics
        service_uuid = btle.UUID("180F")
        temp_characteristic_uuid1 = btle.UUID("2A19")
        humid_characteristic_uuid1 = btle.UUID("2A1C")
        temp_characteristic_uuid2 = btle.UUID("2A1D")
        humid_characteristic_uuid2 = btle.UUID("2A1E")
        
        service = peripheral.getServiceByUUID(service_uuid)
        
        delegate.temp_handle1 = enable_notifications(peripheral, temp_characteristic_uuid1)
        delegate.humid_handle1 = enable_notifications(peripheral, humid_characteristic_uuid1)
        delegate.temp_handle2 = enable_notifications(peripheral, temp_characteristic_uuid2)
        delegate.humid_handle2 = enable_notifications(peripheral, humid_characteristic_uuid2)

        while True:
            if peripheral.waitForNotifications(20.0):
                # Notification received, delegate will handle it
                continue
            print("Waiting...")
    except btle.BTLEDisconnectError as e:
        print(f"Disconnected: {e}")
    finally:
        peripheral.disconnect()  # Close the peripheral connection

def get_sensor_data(target_address):
    peripheral, delegate = connect_to_peripheral(target_address)
    if peripheral:
        receive_data(peripheral, delegate)
        return delegate

if __name__ == "__main__":
    try:
        target_address = "D4:D4:DA:4E:FC:9E"
        delegate = get_sensor_data(target_address)
        if delegate:
            print(f"Final received data - Temp1: {delegate.temperature1}, Humidity1: {delegate.humidity1}, Temp2: {delegate.temperature2}, Humidity2: {delegate.humidity2}")
    finally:
        print("Exiting...")

