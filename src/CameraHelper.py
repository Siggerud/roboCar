from roboCarHelper import map_value_to_new_scale

class CameraHelper:
    def __init__(self):
        self._car = None
        self._servo = None

        self._angleText = ""
        self._speedText = ""
        self._turnText = ""

        self._zoomValue = 1.0
        self._lastStickValue = 0

        self._minZoomValue = 1.0
        self._maxZoomValue = 3.0

        self._zoomButtonMinValue = 0
        self._zoomButtonMaxValue = -1

        self._hudActive = True

        self._controlsDictCamera = {
            "Zoom": "LSB vertical",
            "HUD": "RB"
        }

        self._zoomButton = self._controlsDictCamera["Zoom"]
        self._hudButton = self._controlsDictCamera["HUD"]

        self._turnValue_to_number = {
            "-": 0,
            "Left": 1,
            "Right": 2
        }

    def handle_xbox_input(self, button, pressValue):
        if button == self._zoomButton:
            self._set_zoom_value(pressValue)
        elif button == self._hudButton and pressValue: # check that button is pushed, not released
            self._set_hud_on_or_off()

    def add_car(self, car):
        self._car = car

    def add_servo(self, servo):
        self._servo = servo

    def get_angle_text(self):
        return self._angleText

    def get_speed_text(self):
        return self._speedText

    def get_turn_text(self):
        return self._turnText

    def get_zoom_value(self):
        return self._zoomValue

    def get_hud_value(self):
        return self._hudActive

    def update_control_values_for_video_feed(self, shared_array):
        #TODO: add option for multiple servos
        if self._servo:
            shared_array[0] = self._servo.get_current_servo_angle()

        if self._car:
            shared_array[1] = self._car.get_current_speed()
            shared_array[2] = self._turnValue_to_number[self._car.get_current_turn_value()]

        shared_array[3] = float(self._hudActive)
        shared_array[4] = self._zoomValue

    def camera_buttons(self):
        return self._controlsDictCamera

    def _set_hud_on_or_off(self):
        self._hudActive = not self._hudActive

    def _set_zoom_value(self, buttonPressValue):
        if self._check_if_button_press_within_valid_range(buttonPressValue):
            stickValue = round(buttonPressValue, 1)
        else:
            stickValue = self._zoomButtonMinValue

        if stickValue != self._lastStickValue:
            self._lastStickValue = stickValue
            #with lock:
            self._zoomValue = map_value_to_new_scale(stickValue, self._minZoomValue, self._maxZoomValue, 2,
                                                     self._zoomButtonMinValue, self._zoomButtonMaxValue)


    def _check_if_button_press_within_valid_range(self, buttonPressValue):
        if buttonPressValue >= self._zoomButtonMaxValue and buttonPressValue <= self._zoomButtonMinValue:
            return True
        return False