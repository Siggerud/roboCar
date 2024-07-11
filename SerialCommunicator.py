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

    def read_incoming_data(self):
        serialReading = None
        if self._connection.in_waiting > 0:
            serialReading = self._connection.readline().decode('utf-8').rstrip()

        return serialReading

    def send_command(self, command):
        self._connection.write(command)

    def _port_exists(self, port):
        return os.path.exists(port)

    def cleanup(self):
        self._connection.close()