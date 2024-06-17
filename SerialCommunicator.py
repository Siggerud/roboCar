from serial import Serial
from time import sleep

class SerialCommunicator:
    def __init__(self, port, baudrate):
        self._connection = Serial(port, baudrate)
        sleep(2) # give two seconds for connection to initialize

    def open_communication(self, event):
        while not event.is_set():
            if self._connection.in_waiting > 0:
                print(self._connection.readline().decode('utf-8').rstrip())

        self._connection.close()
