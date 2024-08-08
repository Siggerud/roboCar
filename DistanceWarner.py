from os import path
import RPi.GPIO as GPIO
import serial
from time import sleep, time
from roboCarHelper import map_value_to_new_scale

class DistanceWarner:
    def __init__(self, buzzerPin, port, baudrate, waitTime = 0.25, frontSensor = True, backSensor = True):
        if not self._port_exists(port):
            raise InvalidPortError(f"Port {port} not found. Check connection.")

        self._waitTime = waitTime
        self._frontSensor = frontSensor
        self._backSensor = backSensor

        self._distanceTreshold = 10
        self._encodingType = 'utf-8'

        self._lastReadTime = None
        self._responses = []
        self._withinAlarmDistance = False

        self._honkCurrentlyOn = False
        self._lastHonkChange = time()

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

        GPIO.setup(buzzerPin, GPIO.OUT, initial=self._withinAlarmDistance)
        self._currentLowestDistance = None

        self._serialObj = serial.Serial(port, baudrate)
        sleep(3) # give the serial object some time to start communication

    def alert_if_too_close(self):
        if (time() - self._lastReadTime) < self._waitTime or not self._lastReadTime:
            self._responses.clear()

            if self._frontSensor:
                self._send_command_and_read_response("front")

            if self._backSensor:
                self._send_command_and_read_response("back")

            self._set_honk_value()
            self._set_honk_timing()

            self._lastReadTime = time()

        self._set_honk()

    def cleanup(self):
        self._serialObj.close()

    def _set_honk_value(self):
        if self._check_if_any_response_is_below_threshold():
            self._withinAlarmDistance = True
        else:
            self._withinAlarmDistance = False

    def _set_honk_timing(self):
        if self._withinAlarmDistance:
            timeBetweenEachHonk = map_value_to_new_scale(self._currentLowestDistance, 0.5, 0.1, 1, self._distanceTreshold, 0)
            if (time() - self._lastHonkChange) > timeBetweenEachHonk:
                self._honkCurrentlyOn = not self._honkCurrentlyOn

    def _set_honk(self):
        if not self._withinAlarmDistance:
            GPIO.output(self._buzzerPin, False)
        else:
            GPIO.output(self._buzzerPin, self._honkCurrentlyOn)

    def _check_if_any_response_is_below_threshold(self):
        self._currentLowestDistance = min(self._responses)
        if self._currentLowestDistance < self._distanceTreshold:
            return True

        return False

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




