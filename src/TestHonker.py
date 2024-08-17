import unittest
from unittest.mock import patch, call
from Honker import Honker
import RPi.GPIO as GPIO

@patch("RPi.GPIO.setup")
class TestHonker(unittest.TestCase):
    buzzerPin = 1
    def get_honker_object(self):
        return Honker(self.buzzerPin)

    def test_init_calls(self, mock_setup):
        honker = self.get_honker_object()

        mock_setup.assert_has_calls(
            call(self.buzzerPin, GPIO.OUT, initial=False)
        )

    def test_check_if_any_response_is_below_treshold(self, mock_setup):
        honker = self.get_honker_object()

        # check that it returns true when one value is below treshold
        sensorValues = [19, 302, None, 9.9, 18]
        result = honker._check_if_any_response_is_below_threshold(sensorValues)

        assert result

        # check that it returns false when noe values are below treshold
        sensorValues = [10.1, 10, None, 22]
        result = honker._check_if_any_response_is_below_threshold(sensorValues)

        assert(not result)

if __name__ == '__main__':
    unittest.main()
