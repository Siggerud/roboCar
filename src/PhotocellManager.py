import RPi.GPIO as GPIO
from roboCarHelper import map_value_to_new_scale

class PhotocellManager:
    def __init__(self, lightPins):
        pwmFrequency = 100
        self._pwms = []
        for pin in lightPins:
            #GPIO.setup(pin, GPIO.OUT)
            
            pwm = "a"
            #pwm = GPIO.PWM(pin, pwmFrequency)
            self._pwms.append(pwm)

        self._minLightSensorValue = 0
        self._maxLightSensorValue = 1023

        self._minPwmValue = 0
        self._maxPwmValue = 99
        self._currentPwmValue = 0


    def adjust_car_lights_to_external_lights(self):
        for pwm in self._pwms:
            #pwm.ChangeDutyCycle(self._currentPwmValue)
            print(self._currentPwmValue)

    def prepare_for_light_adjustment(self, lightSensorValue):
        # the car lights pwm value have an inverse relationship to the light sensor value
        self._currentPwmValue = map_value_to_new_scale(
            lightSensorValue,
            self._minPwmValue,
            self._maxPwmValue,
            0,
            self._maxLightSensorValue,
            self._minLightSensorValue
        )

    def cleanup(self):
        for pwm in self._pwms:
            #pwm.stop()
            print("messed up loop")


