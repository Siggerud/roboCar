import unittest
from unittest.mock import patch, MagicMock

# mock the import of RPi.GPIO
MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

from honker import Honker
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setup")
class TestHonker(unittest.TestCase):
    buzzerPin = 1

    def test_setup(self, mock_gpioSetup):
        honker = Honker(self.buzzerPin)
        honker.setup()

        # assert that the GPIO.setup method is called with expected parameters
        mock_gpioSetup.assert_called_once_with(self.buzzerPin, GPIO.OUT, initial=False)

    @patch("RPi.GPIO.output")
    def test_honker_does_not_honk_when_outside_treshold(self, mock_gpioOutput, mock_gpioSetup):
        honker = Honker(self.buzzerPin)

        honker.setup()

        # set treshold to be 15 cm
        honker.set_distance_treshold(15)

        distances = [16, 21, None]
        honker.prepare_for_honking(distances)
        honker.alert_if_too_close()

        # assert that the buzzer is not turned on
        mock_gpioOutput.assert_called_once_with(self.buzzerPin, False)

    @patch("RPi.GPIO.output")
    def test_honker_does_honk_when_inside_treshold(self, mock_gpioOutput, mock_gpioSetup):
        honker = Honker(self.buzzerPin)

        honker.setup()

        # set treshold to be 15 cm
        honker.set_distance_treshold(15)

        distances = [None, 21, 14]
        honker.prepare_for_honking(distances)
        honker.alert_if_too_close()

        # assert that the buzzer is not turned on
        mock_gpioOutput.assert_called_once_with(self.buzzerPin, True)

    @patch("RPi.GPIO.output")
    @patch("honker.time")
    def test_honker_beeps(self, mock_time, mock_gpioOutput, mock_gpioSetup):
        # mock the outputs of the time function
        mock_time.side_effect = [0, 1]

        honker = Honker(self.buzzerPin)

        honker.setup()

        # set treshold to be 15 cm
        honker.set_distance_treshold(15)

        distances = [None, 21, 14]
        honker.prepare_for_honking(distances)

        # run the prepare_for_honking function twice to check if it turns off buzzer after a while
        honker.alert_if_too_close()
        honker.alert_if_too_close()

        # assert that buzzer will turn off after a given time
        mock_gpioOutput.assert_called_with(self.buzzerPin, False)

if __name__ == '__main__':
    unittest.main()
