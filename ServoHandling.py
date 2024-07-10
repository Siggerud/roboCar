from roboCarHelper import scale_button_press_value
import pigpio

class ServoHandling:
    def __init__(self, servoPin):
        self._servoPin = servoPin
        self._pigpioPwm = pigpio.pi()
        self._pigpioPwm.set_mode(servoPin, pigpio.OUTPUT)
        self._pigpioPwm.set_PWM_frequency(servoPin, 50)

        self._lastServoStickValue = 0
        self._servoValueChanged = False
        self._servoPwmValue = 0
        self._pwmMinServo = 2500
        self._pwmMaxServo = 500

        self._moveServoButtons = [
            "RSB horizontal"
        ]

    def handle_xbox_input(self, buttonAndPressValue):
        button, buttonPressValue = buttonAndPressValue
        if button in self._moveServoButtons:
            self._prepare_for_servo_movement(buttonPressValue)
            self._move_servo()

    def _move_servo(self):
        if self._servoValueChanged:
            self._pigpioPwm.set_servo_pulsewidth(self._servoPin, self._servoPwmValue)

    def _prepare_for_servo_movement(self, buttonPressValue):
        stickValue = round(buttonPressValue, 1)

        if stickValue == self._lastServoStickValue:
            self._servoValueChanged = False
        else:
            self._servoValueChanged = True
            self._servoPwmValue = scale_button_press_value(stickValue, self._pwmMinServo, self._pwmMaxServo, 1)
            self._lastServoStickValue = stickValue

    def cleanup(self):
        self._pigpioPwm.set_PWM_dutycycle(self._servoPin, 0)
        self._pigpioPwm.set_PWM_frequency(self._servoPin, 0)