import unittest
from unittest.mock import patch, MagicMock
from ServoHandling import ServoHandling
from roboCarHelper import map_value_to_new_scale
import pigpio

@patch("pigpio.pi")
class TestServoHandling(unittest.TestCase):
    # define GPIO pins
    servoPin = 26

    def test_init(self, mock_pi):
        #make a mock instance to check if pigpio methods have been called on it
        mock_instance = MagicMock()
        mock_pi.return_value = mock_instance

        # initialize servo
        servo = ServoHandling(self.servoPin)

        # assert that pi method has been called
        mock_pi.assert_called_once()

        #assert that methods have been called on mock object
        mock_instance.set_mode.assert_called_with(self.servoPin, pigpio.OUTPUT)
        mock_instance.set_PWM_frequency.assert_called_with(self.servoPin, 50)

        # assert that class instance values are as expected
        self.assertEqual(servo._lastServoStickValue, 0)
        self.assertEqual(servo._servoValueChanged, False)
        self.assertEqual(servo._servoPwmValue, 1500)
        self.assertEqual(servo._pwmMinServo, 2500)
        self.assertEqual(servo._pwmMaxServo, 500)
        self.assertEqual(servo._controlsDictServo, {"Servo": "RSB horizontal"})
        self.assertEqual(servo._moveServoButton, "RSB horizontal")

    def test_prepare_for_servo_movement(self, mock_pi):
        # initialize servo
        servo = ServoHandling(self.servoPin)

        inputValue = 0.8
        servo._prepare_for_servo_movement(inputValue)

        self.assertEqual(servo._servoValueChanged, True)
        self.assertEqual(servo._servoPwmValue, map_value_to_new_scale(inputValue, servo._pwmMinServo, servo._pwmMaxServo, 1))
        self.assertEqual(servo._lastServoStickValue, inputValue)


if __name__ == '__main__':
    unittest.main()