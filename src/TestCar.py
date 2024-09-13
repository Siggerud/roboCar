import unittest
from unittest.mock import patch, call, Mock, MagicMock

# mock the import of RPi.GPIO
MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from CarHandling import CarHandling
import RPi.GPIO as GPIO

class TestCarHandling(unittest.TestCase):
    # define GPIO pins
    rightForward = 1
    rightBackward = 2
    leftForward = 3
    leftBackward = 4
    enA = 5
    enB = 6

    minPwm = 10
    maxPwm = 40

    def get_car(self):
        return CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB,
            self.minPwm,
            self.maxPwm
        )

    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.setmode")
    def test_setup(self, mock_setmode, mock_setup, mock_pwm):
        car = self.get_car()
        car.setup()

        carPins = [
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        ]

        calls = [
            call(pin, GPIO.OUT) for pin in carPins
        ]

        # check that GPIO.setup is called correctly for all pins
        mock_setup.assert_has_calls(calls, any_order=False)

        calls = [
            call(pin, 100) for pin in carPins[4:]
        ]

        #check that pwm is called with correct pins and frequency
        mock_pwm.assert_has_calls(calls, any_order=False)

    def test_get_car_buttons(self):
        car = self.get_car()

        result = car.get_car_buttons()["Right"]
        self.assertEqual("D-PAD right", result)

        result = car.get_car_buttons()["Reverse"]
        self.assertEqual("LT", result)

    @patch("RPi.GPIO.cleanup")
    def test_cleanup(self, mock_cleanup):
        car = self.get_car()

        pwmA = Mock()
        pwmB = Mock()

        # set the car PWM objects to be mocks, so we can track calls
        car._pwmA = pwmA
        car._pwmB = pwmB

        car.cleanup()

        # check that the stop method is run on the PWM objects
        pwmA.stop.assert_called_once()
        pwmB.stop.assert_called_once()

        # check that GPIO cleanup is run
        mock_cleanup.assert_called_once()

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_turns_car(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "D-PAD left"
        pressValue = 1

        pwmA = Mock()
        pwmB = Mock()

        car = self.get_car()
        car.setup()

        car._pwmA = pwmA
        car._pwmB = pwmB

        car.handle_xbox_input(button, pressValue)

        # assert that ChangeDutyCycle is called on both PWMs with max speed
        pwmA.ChangeDutyCycle.assert_called_once_with(self.maxPwm)
        pwmB.ChangeDutyCycle.assert_called_once_with(self.maxPwm)

        calls = [
            call(self.leftForward, GPIO.LOW),
            call(self.rightForward, GPIO.HIGH),
            call(self.leftBackward, GPIO.HIGH),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert HIGH and LOW calls to pins
        mock_output.assert_has_calls(calls, any_order=True)

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_stops_turning_car(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "D-PAD right"
        pressValue = 0

        car = self.get_car()
        car.setup()

        car.handle_xbox_input(button, pressValue)

        calls = [
            call(self.leftForward, GPIO.LOW),
            call(self.rightForward, GPIO.LOW),
            call(self.leftBackward, GPIO.LOW),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert HIGH and LOW calls to pins
        mock_output.assert_has_calls(calls, any_order=True)

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_turns_right_while_reversing(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "D-PAD right"
        pressValue = 1

        pwmA = Mock()
        pwmB = Mock()

        car = self.get_car()
        car.setup()

        # set goReverse to be true to simulate the car being in reverse mode
        car._goReverse = True

        car._pwmA = pwmA
        car._pwmB = pwmB

        car.handle_xbox_input(button, pressValue)

        # assert that ChangeDutyCycle is not called since the car should not do this for turns while in motion
        pwmA.ChangeDutyCycle.assert_not_called()
        pwmB.ChangeDutyCycle.assert_not_called()

        calls = [
            call(self.leftForward, GPIO.LOW),
            call(self.rightForward, GPIO.LOW),
            call(self.leftBackward, GPIO.HIGH),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert HIGH and LOW calls to pins
        mock_output.assert_has_calls(calls, any_order=True)

    @patch("RPi.GPIO.setmode")
    @patch("RPi.GPIO.PWM")
    @patch("RPi.GPIO.setup")
    @patch("RPi.GPIO.output")
    def test_handle_xbox_input_sets_correct_pwm_to_press_value(self, mock_output, mock_setup, mock_pwm, mock_setmode):
        button = "RT"
        pressValue = 0 # 50 % of max throttle

        car = self.get_car()
        car.setup()

        pwmA = Mock()
        pwmB = Mock()

        car._pwmA = pwmA
        car._pwmB = pwmB

        car.handle_xbox_input(button, pressValue)

        # assert that ChangeDutyCycle is called on both PWMs with value right between min and max value
        halfPowerPwm = round((self.maxPwm + self.minPwm) / 2, 2)

        pwmA.ChangeDutyCycle.assert_called_once_with(halfPowerPwm)
        pwmB.ChangeDutyCycle.assert_called_once_with(halfPowerPwm)

        calls = [
            call(self.leftForward, GPIO.HIGH),
            call(self.rightForward, GPIO.HIGH),
            call(self.leftBackward, GPIO.LOW),
            call(self.rightBackward, GPIO.LOW)
        ]

        # assert forward pins are called
        mock_output.assert_has_calls(calls, any_order=True)

    """
    def get_car_object(self):
        car = CarHandling(
            self.leftBackward,
            self.leftForward,
            self.rightBackward,
            self.rightForward,
            self.enA,
            self.enB
        )

        return car

    def test_init(self, mock_pwm, mock_setup):
        car = self.get_car_object()

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

    @patch.object(CarHandling, "_change_duty_cycle", autospec=True)
    def test_prepare_car_for_turning(self, mock_dutyCycle, mock_pwm, mock_setup):
        car = self.get_car_object()
        car._pwmMaxTT = 90
        car._goForward = True # simulate that the car is in motion

        button = "D-PAD left"
        car._prepare_car_for_turning(button)

        assert(car._turnLeft)
        assert(not car._turnRight)
        mock_dutyCycle.assert_not_called()

        button = "D-PAD right"
        car._prepare_car_for_turning(button)

        assert(not car._turnLeft)
        assert(car._turnRight)
        mock_dutyCycle.assert_not_called()

        car._goForward = False # simulate that the car is stationary

        car._prepare_car_for_turning(button)
        mock_dutyCycle.assert_called_with(car, [car._pwmA, car._pwmB], 90)

    @patch.object(CarHandling, "_change_duty_cycle", autospec=True)
    @patch("CarHandling.map_value_to_new_scale", autospec=True)
    def test_prepare_car_for_throttle(self, mock_mapping, mock_dutyCycle, mock_pwm, mock_setup):
        mock_mapping.return_value = 8 # this will be the speed, which is below minPWM

        car = self.get_car_object()
        car._pwmMinTT = 10

        car._prepare_car_for_throttle("RT", 0.1)

        assert(not car._goForward)
        assert(not car._goReverse)
        assert(car._speed == 0)
        mock_dutyCycle.assert_called_with(car, [car._pwmA, car._pwmB], 0)

        mock_mapping.return_value = 12  # this will be the speed, which is above minPWM

        car._prepare_car_for_throttle("RT", 0.1)

        assert(car._goForward)
        assert(not car._goReverse)
        assert(car._speed == 12)
        mock_dutyCycle.assert_called_with(car, [car._pwmA, car._pwmB], 12)

        car._prepare_car_for_throttle("LT", 0.1)

        assert(not car._goForward)
        assert(car._goReverse)
        assert(car._speed == 12)
        mock_dutyCycle.assert_called_with(car, [car._pwmA, car._pwmB], 12)

    def test_cleanup(self, mock_pwm, mock_setup):
        car = self.get_car_object()

        # create mock pwm objects
        mockPwmA = Mock()
        mockPwmB = Mock()

        # assign mock objects to car instance variables
        car._pwmA = mockPwmA
        car._pwmB = mockPwmB

        # run method to test
        car.cleanup()

        mockPwmA.stop.assert_called_once()
        mockPwmB.stop.assert_called_once()

    def test_adjust_gpio_values(self, mock_pwm, mock_setup):
        with patch("RPi.GPIO.output") as mock_output:
            car = self.get_car_object()

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
        car = self.get_car_object()

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
        mockPwmB.ChangeDutyCycle.assert_called_with(speed)"""


if __name__ == '__main__':
    unittest.main()