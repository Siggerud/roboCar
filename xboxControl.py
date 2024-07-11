import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess
from time import sleep

class XboxControl:
    def __init__(self):
        self._car = None
        self._camera = None
        self._servo = None
        self._distanceWarner = None

        self._joyHatMotionToButtons = {
            -1: "D-PAD left",
            1: "D-PAD right",
            0: "D-PAD released"
        }

        self._joyAxisMotionToButtons = {
            0: "LSB horizontal",
            1: "LSB vertical",
            2: "RSB horizontal",
            3: "RSB vertical",
            4: "RT",
            5: "LT",

        }

        self._x11Connected = self._check_if_X11_connected()
        if not self._x11Connected:
            return

        self._controller = self._set_controller()
        if self._controller:
            self._print_battery_status_of_controller()

    def start_controller(self, threadEvent):
        if not self._x11Connected:
            print("X11 not found. Open VcSrv")
            return

        if not self._controller:
            print("No controller detected. Turn on xbox controller")
            return

        while not threadEvent.is_set():
            for event in pygame.event.get():
                buttonAndPressValue = self._get_button_and_press_value_from_event(event)
                if self._car:
                    self._car.handle_xbox_input(buttonAndPressValue)
                if self._servo:
                    self._servo.handle_xbox_input(buttonAndPressValue)
                if self._camera:
                    self._camera.handle_xbox_input(buttonAndPressValue)
            if self._distanceWarner:
                self._distanceWarner.listen_for_incoming_sensor_data()

        if self._car:
            self._car.cleanup()

        if self._servo:
            self._servo.cleanup()

        if self._camera:
            self._camera.cleanup()

    def _get_button_and_press_value_from_event(self, event):
        button = None
        buttonPressValue = None

        eventType = event.type
        if eventType == pygame.JOYHATMOTION:
            button = self._joyHatMotionToButtons[self._controller.get_hat(0)[0]] # horizontal
        elif eventType == pygame.JOYAXISMOTION:
            axis = event.axis
            button = self._joyAxisMotionToButtons[axis]
            buttonPressValue = self._controller.get_axis(axis)

        return (button, buttonPressValue)


    def _set_controller(self):
        controller = None

        pygame.init()
        pygame.joystick.init()

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            controller = pygame.joystick.Joystick(0)
            controller.init()
            print("Controller connected: ", controller.get_name())

        return controller

    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server")

        return not returnCode

    def _print_battery_status_of_controller(self):
        self._controller.rumble()
        sleep(0.5)
        self._controller.stop_rumble()

    def add_distance_warner(self, distanceWarner):
        self._distanceWarner = distanceWarner

    def add_car(self, car):
        self._car = car

    def add_camera(self, camera):
        self._camera = camera
        self._camera.start_preview()

    def add_servo(self, servo):
        self._servo = servo