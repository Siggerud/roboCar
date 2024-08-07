from os import path
import RPi.GPIO as GPIO
import serial
from time import sleep
from roboCarHelper import map_value_to_new_scale

class DistanceWarner:
    def __init__(self, buzzerPin, port, baudrate, sleepTime = 0.1, frontSensor = True, backSensor = True):
        if not self._port_exists(port):
            raise InvalidPortError(f"Port {port} not found. Check connection.")

        self._sleepTime = sleepTime
        self._frontSensor = frontSensor
        self._backSensor = backSensor

        self._distanceTreshold = 10
        self._encodingType = 'utf-8'

        self._lastReadTime = None
        self._responses = []
        self._currentLowestDistance = None

        self._turnButtons = [
            "D-PAD left",
            "D-PAD right",
            "D-PAD released"
        ]

        self._gasAndReverseButtons = [
            "RT",
            "LT",
        ]

        self._buzzerPin = buzzerPin

        GPIO.setup(buzzerPin, GPIO.OUT)
        self._lowestFrequency = 25
        self._highestFrequency = 1000
        self._lastFrequency = self._highestFrequency
        self._lastDutyCycle = 0
        self._buzzer = GPIO.PWM(buzzerPin, self._lastFrequency)
        self._buzzer.start(self._lastDutyCycle)

        self._serialObj = serial.Serial(port, baudrate)
        sleep(3) # give the serial object some time to start communication

    def alert_if_too_close(self):
        self._responses.clear()

        if self._frontSensor:
            self._send_command_and_read_response("front")

        if self._backSensor:
            self._send_command_and_read_response("back")

        self._set_current_lowest_distance()
        self._set_honk()
        self._honk_if_too_close()

        sleep(self._sleepTime)

    def cleanup(self):
        self._buzzer.stop()
        self._serialObj.close()

    def _set_honk(self):
        if self._check_if_response_is_below_threshold():
            dutyCycle = 50
        else:
            dutyCycle = 0

        if dutyCycle != self._lastDutyCycle:
            self._buzzer.ChangeDutyCycle(dutyCycle)
            self._lastDutyCycle = dutyCycle

    def _honk_if_too_close(self):
        if self._lastDutyCycle != 0:
            frequency = map_value_to_new_scale(self._currentLowestDistance, self._highestFrequency, self._lowestFrequency, 1, self._distanceTreshold, 0)

            if frequency != self._lastFrequency:
                self._buzzer.ChangeFrequency(frequency)
                self._lastFrequency = frequency

    def _check_if_response_is_below_threshold(self):
        if self._currentLowestDistance < self._distanceTreshold:
            return True

        return False

    def _set_current_lowest_distance(self):
        self._currentLowestDistance = min(self._responses)

    def _send_command_and_read_response(self, command):
        # send command to arduino
        self._serialObj.write(self._make_commands_arduino_readable(command))

        # wait for arduino response
        self._wait_for_arduino_input()

        # print out arduino response
        response = float(self._make_arduino_response_readable(self._serialObj.readline()))
        self._responses.append(response)

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




