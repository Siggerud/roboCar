import unittest
from unittest.mock import patch, call, Mock
from CarHandling import CarHandling
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setup")
@patch("RPi.GPIO.PWM")
class TestCarHandling(unittest.TestCase):
    # define GPIO pins
    rightForward = 22  # IN2
    rightBackward = 18  # IN1
    leftForward = 16  # IN4
    leftBackward = 15  # IN3
    enA = 11
    enB = 13

    def initialize_car(self):
        car = CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        )




    def test_init(self, mock_pwm, mock_setup):
        car = self.initialize_car()

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

    def test_adjust_gpio_values(self, mock_pwm, mock_setup):
        with patch("RPi.GPIO.output") as mock_output:
            car = CarHandling(
                self.leftBackward,
                self.leftForward,
                self.rightBackward,
                self.rightForward,
                self.enA,
                self.enB
            )

            # values that will set the GPIO state of each motor
            gpioValues = [True, True, False, False]

            # call method we want to test
            car._adjust_gpio_values(gpioValues)

            # check that GPIO.output has been called on expected pins
            mock_output.assert_has_calls(
                [
                    call(self.leftForward, GPIO.HIGH),
                    call(self.rightForward, GPIO.HIGH),
                    call(self.leftBackward, GPIO.LOW),
                    call(self.rightBackward, GPIO.LOW),
                ],
                any_order=True
            )

    def test_change_duty_cycle(self, mock_pwm, mock_setup):
        car = CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        )

        # create mock pwm objects
        mockPwmA = Mock()
        mockPwmB = Mock()

        # assign mock objects to car instance variables
        car._pwmA = mockPwmA
        car._pwmB = mockPwmB

        speed = 50

        # call the method we want to test
        car._change_duty_cycle([car._pwmA, car._pwmB], speed)

        # check that the ChangeDutyCycle has been called on the mock object
        mockPwmA.ChangeDutyCycle.assert_called_with(speed)
        mockPwmB.ChangeDutyCycle.assert_called_with(speed)


if __name__ == '__main__':
    unittest.main()