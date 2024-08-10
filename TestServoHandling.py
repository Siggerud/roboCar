import unittest
from unittest.mock import patch, MagicMock
from ServoHandling import ServoHandling
import pigpio

@patch("pigpio.pi")
class TestServoHandling(unittest.TestCase):
    # define GPIO pins
    servoPin = 26

    def test_init(self, mock_pi):
        mock_instance = MagicMock()
        mock_pi.return_value = mock_instance

        servo = ServoHandling(self.servoPin)

        mock_pi.assert_called_once()

        mock_instance.set_mode.assert_called_with(self.servoPin, pigpio.OUTPUT)

        mock_instance.set_PWM_frequency.assert_called_with(self.servoPin, 50)

        self.assertEqual(servo._lastServoStickValue, 0)
        self.assertEqual(servo._servoValueChanged, False)
        self.assertEqual(servo._servoPwmValue, 1500)
        self.assertEqual(servo._pwmMinServo, 2500)
        self.assertEqual(servo._pwmMaxServo, 500)
        self.assertEqual(servo._controlsDictServo, {"Servo": "RSB horizontal"})
        self.assertEqual(servo._moveServoButton, "RSB horizontal")


if __name__ == '__main__':
    unittest.main()