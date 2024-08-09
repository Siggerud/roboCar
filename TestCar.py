import unittest
from unittest.mock import patch, call
from CarHandling import CarHandling

class TestMoterManager(unittest.TestCase):
    # define GPIO pins
    rightForward = 22  # IN2
    rightBackward = 18  # IN1
    leftForward = 16  # IN4
    leftBackward = 15  # IN3
    enA = 11
    enB = 13

    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.PWM")
    def test_init(self, mock_output):


        car = CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        )

        mock_output.assert_has_calls([call(self.leftBackward, True), call(self.leftForward, True)], any_order=True)

