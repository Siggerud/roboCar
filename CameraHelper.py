class CameraHelper:
    def __init__(self):
        self._car = None
        self._servo = None

        self._angleText = ""
        self._speedText = ""
        self._turnText = ""

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

    def update_control_values_for_video_feed(self, lock):
        with lock:
            if self._servo:
                self._angleText = "Angle: " + str(self._servo.get_current_servo_angle())

            if self._car:
                self._speedText = "Speed: " + str(self._car.get_current_speed()) + "%"
                self._turnText = "Turn: " + self._car.get_current_turn_value()