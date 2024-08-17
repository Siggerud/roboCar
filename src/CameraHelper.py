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

    def handle_xbox_input(self, buttonAndValue, lock):
        button, buttonPressValue = buttonAndValue
        if button == self._zoomButton:
            self._set_zoom_value(buttonPressValue, lock)
        elif button == self._hudButton and buttonPressValue: # check that button is pushed, not released
            self._set_hud_on_or_off(lock)

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

    def update_control_values_for_video_feed(self, lock):
        with lock:
            if self._servo:
                self._angleText = "Angle: " + str(self._servo.get_current_servo_angle())

            if self._car:
                self._speedText = "Speed: " + str(self._car.get_current_speed()) + "%"
                self._turnText = "Turn: " + self._car.get_current_turn_value()

    def camera_buttons(self):
        return self._controlsDictCamera

    def _set_hud_on_or_off(self, lock):
        with lock:
            self._hudActive = not self._hudActive

    def _set_zoom_value(self, buttonPressValue, lock):
        if self._check_if_button_press_within_valid_range(buttonPressValue):
            stickValue = round(buttonPressValue, 1)
        else:
            stickValue = self._zoomButtonMinValue

        if stickValue != self._lastStickValue:
            self._lastStickValue = stickValue
            with lock:
                self._zoomValue = map_value_to_new_scale(stickValue, self._minZoomValue, self._maxZoomValue, 2,
                                                     self._zoomButtonMinValue, self._zoomButtonMaxValue)


    def _check_if_button_press_within_valid_range(self, buttonPressValue):
        if buttonPressValue >= self._zoomButtonMaxValue and buttonPressValue <= self._zoomButtonMinValue:
            return True
        return False