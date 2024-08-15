from os import path
import RPi.GPIO as GPIO
import serial
from time import sleep, time
from roboCarHelper import map_value_to_new_scale
from Honker import Honker

class ArduinoCommunicator:
    def __init__(self, port, baudrate, waitTime = 0.1):
        if not self._port_exists(port):
            raise InvalidPortError(f"Port {port} not found. Check connection.")

        self._waitTime = waitTime
        self._frontSensor = False
        self._backSensor = False
        self._honker = None

        self._frontSensorReading = None
        self._backSensorReading = None

        self._encodingType = 'utf-8'

        self._lastReadTime = None

        self._serialObj = serial.Serial(port, baudrate)
        sleep(3) # give the serial object some time to start communication

    def activate_distance_sensors(self, buzzerPin, front=True, back=True):
        self._frontSensor = front
        self._backSensor = back

        self._honker = Honker(buzzerPin)

    def start(self):
        # if it's been more than the specified wait time since last reading, then
        # do a new reading
        if not self._lastReadTime or (time() - self._lastReadTime) < self._waitTime:

            if self._frontSensor:
                self._frontSensorReading = self._send_command_and_read_response("front")

            if self._backSensor:
                self._backSensorReading = self._send_command_and_read_response("back")

            if self._frontSensor or self._backSensor:
                self._honker.prepare_for_honking(
                    [self._frontSensorReading,
                    self._backSensorReading]
                )

            self._lastReadTime = time()  # update last read time

        if self._frontSensor or self._backSensor:
            self._honker.alert_if_too_close()

    def cleanup(self):
        self._serialObj.close()

    def _send_command_and_read_response(self, command):
        # send command to arduino
        self._serialObj.write(self._make_commands_arduino_readable(command))

        # wait for arduino response
        self._wait_for_arduino_input()

        # print out arduino response
        reading = float(self._make_arduino_response_readable(self._serialObj.readline()))

        return reading

    def _make_commands_arduino_readable(self, command):
        return (command + "\n").encode(self._encodingType)

    def _make_arduino_response_readable(self, response):
        return response.decode(self._encodingType).rstrip()

    def _wait_for_arduino_input(self):
        while self._serialObj.in_waiting <= 0:
            sleep(0.01)

    def _port_exists(self, portPath):
        return path.exists(portPath)

class InvalidPortError(Exception):
    pass




