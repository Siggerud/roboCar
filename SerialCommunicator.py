from serial import Serial
from time import sleep
import os.path

class SerialCommunicator:
    def __init__(self, port, baudrate):
        if self._port_exists(port):
            self._port_valid = True

            self._connection = Serial(port, baudrate)
            sleep(2) # give two seconds for connection to initialize

            print(f"Succesful port connection. Connected to {port}")
        else:
            self._port_valid = False

            print("No port found. Check connections.")

    def open_communication(self, event):
        if not self._port_valid:
            return

        while not event.is_set():
            if self._connection.in_waiting > 0:
                print(self._connection.readline().decode('utf-8').rstrip())

        self._connection.close()

    def _port_exists(self, port):
        return os.path.exists(port)