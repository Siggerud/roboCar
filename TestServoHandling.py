import unittest
from unittest.mock import patch, call, Mock
from ServoHandling import ServoHandling
import pigpio

@patch("pigpio.pi")
@patch("pigpio.set_mode")
@patch("set_PWM_frequency")
class TestServoHandling(unittest.TestCase):
    # define GPIO pins
    servoPin = 26

    def test_init(self, mock_pwm_frequency, mock_set_mode, mock_pi):
        servo = ServoHandling(self.servoPin)

        mock_pwm_frequency.assert_has_calls(
            [
                call(self.servoPin, 50),
            ]
        )

        mock_set_mode.assert_has_calls(
            [
                call(self.servoPin, pigpio.OUTPUT)
            ]
        )

        mock_pi.assert_called_once()