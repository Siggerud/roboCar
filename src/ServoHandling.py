from roboCarHelper import map_value_to_new_scale
import pigpio

class ServoHandling:
    def __init__(self, servoPin):
        self._servoPin = servoPin
        self._pigpioPwm = pigpio.pi()
        self._pigpioPwm.set_mode(servoPin, pigpio.OUTPUT)
        self._pigpioPwm.set_PWM_frequency(servoPin, 50)

        self._lastServoStickValue = 0
        self._servoValueChanged = False
        self._servoPwmValue = 1500
        self._pwmMinServo = 2500
        self._pwmMaxServo = 500

        self._controlsDictServo = {
            "Servo": "RSB horizontal"
        }

        self._moveServoButton = self._controlsDictServo["Servo"]

    def handle_xbox_input(self, buttonAndPressValue):
        button, buttonPressValue = buttonAndPressValue
        if button == self._moveServoButton:
            self._prepare_for_servo_movement(buttonPressValue)
            self._move_servo()

    def update_control_values_for_video_feed(self, lock, shared_dict):
        with lock:
            shared_dict['angle'] = self.get_current_servo_angle()

    def servo_buttons(self):
        return self._controlsDictServo

    def get_current_servo_angle(self):
        current_servo_angle = int(map_value_to_new_scale(self._servoPwmValue, -90, 90, 0, self._pwmMinServo, self._pwmMaxServo))

        return current_servo_angle

    def _move_servo(self):
        if self._servoValueChanged:
            self._pigpioPwm.set_servo_pulsewidth(self._servoPin, self._servoPwmValue)

    def _prepare_for_servo_movement(self, buttonPressValue):
        stickValue = round(buttonPressValue, 1)

        if stickValue == self._lastServoStickValue:
            self._servoValueChanged = False
        else:
            self._servoValueChanged = True
            self._servoPwmValue = map_value_to_new_scale(stickValue, self._pwmMinServo, self._pwmMaxServo, 1)
            self._lastServoStickValue = stickValue

    def cleanup(self):
        self._pigpioPwm.set_PWM_dutycycle(self._servoPin, 0)
        self._pigpioPwm.set_PWM_frequency(self._servoPin, 0)