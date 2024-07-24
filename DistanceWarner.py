import RPi.GPIO as GPIO
import serial
from time import sleep


class DistanceWarner:
    def __init__(self, buzzerPin, port, baudrate, frontSensor = True, backSensor = True):
        self._distanceTreshold = 10
        self._encodingType = 'utf-8'
        self._frontSensor = frontSensor
        self._backSensor = backSensor
        self._responses = []
        self._honkValue = False

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

        GPIO.setup(buzzerPin, GPIO.OUT, initial=self._honkValue)

        self._serialObj = serial.Serial(port, baudrate)
        sleep(3)

    def handle_xbox_input(self, buttonAndPressValue):
        button, buttonPressValue = buttonAndPressValue
        if button in self._turnButtons or button in self._gasAndReverseButtons:
            self._alert_if_too_close()



    def _alert_if_too_close(self):
        self._responses.clear()

        if self._frontSensor:
            self._send_command_and_read_response("front")

        if self._backSensor:
            self._send_command_and_read_response("back")

        self._set_honk_value()
        self._set_honk()

    def _set_honk_value(self):
        if self._check_if_any_response_is_below_threshold():
            self._honkValue = True
        else:
            self._honkValue = False

    def _set_honk(self):
        GPIO.output(self._buzzerPin, self._honkValue)

    def _check_if_any_response_is_below_threshold(self):
        for response in self._responses:
            if response < self._distanceTreshold:
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

    def cleanup(self):
        self._serialObj.close()

