import unittest
from unittest.mock import patch, call
from CarHandling import CarHandling
import RPi.GPIO as GPIO

class TestCarHandling(unittest.TestCase):
    # define GPIO pins
    rightForward = 22  # IN2
    rightBackward = 18  # IN1
    leftForward = 16  # IN4
    leftBackward = 15  # IN3
    enA = 11
    enB = 13

    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.PWM")
    def test_init(self, mock_pwm, mock_setup):
        car = CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        )

        # check that GPIO setup has been called with expected pins
        mock_setup.assert_has_calls(
            [
            call(self.leftBackward, GPIO.OUT),
            call(self.leftForward, GPIO.OUT),
            call(self.rightForward, GPIO.OUT),
            call(self.rightBackward, GPIO.OUT),
            call(self.enA, GPIO.OUT),
            call(self.enB, GPIO.OUT)
            ],
            any_order=True
        )

        # check that GPIO.PWM has been called with expected pins
        mock_pwm.assert_has_calls(
            [
                call(self.enA, 100),
                call(self.enB, 100)],
                any_order=True
        )


if __name__ == '__main__':
    unittest.main()