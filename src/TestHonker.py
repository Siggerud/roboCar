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
            call(self.buzzerPin, GPIO.OUT)
        )


if __name__ == '__main__':
    unittest.main()
