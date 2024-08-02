import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess
from threading import Thread

class XboxControl:
    def __init__(self):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._controller = self._set_controller()

        self._car = None
        self._camera = None
        self._servo = None
        self._distanceWarner = None
        self._threads = []

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

    def activate_distance_warner(self, event):
        thread = Thread(target=self._listen_for_distance_warnings, args=(event,))
        self._threads.append(thread)
        thread.start()

    def activate_car_controlling(self, event):
        thread = Thread(target=self._start_controller, args=(event,))
        self._threads.append(thread)
        thread.start()

    def cleanup(self):
        # close all threads
        for thread in self._threads:
            thread.join()

        if self._car:
            self._car.cleanup()

        if self._servo:
            self._servo.cleanup()

        if self._camera:
            self._camera.cleanup()

        if self._distanceWarner:
            self._distanceWarner.cleanup()

    def _start_controller(self, threadEvent):
        while not threadEvent.is_set():
            for event in pygame.event.get():
                buttonAndPressValue = self._get_button_and_press_value_from_event(event)
                if self._car:
                    self._car.handle_xbox_input(buttonAndPressValue)
                if self._servo:
                    self._servo.handle_xbox_input(buttonAndPressValue)
                if self._camera:
                    self._set_control_values()
                    self._camera.handle_xbox_input(buttonAndPressValue)

    def _set_control_values(self):
        if self._servo:
            currentServoAngle = self._servo.get_current_servo_angle()
            self._camera.set_current_servo_angle(currentServoAngle)

        if self._car:
            currentSpeed = self._car.get_current_speed()
            self._camera.set_current_car_speed(currentSpeed)

            currentTurnValue = self._car.get_current_turn_value()
            self._camera.set_current_turn_value(currentTurnValue)

    def _listen_for_distance_warnings(self, threadEvent):
        while not threadEvent.is_set():
            self._distanceWarner.alert_if_too_close()

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
        pygame.init()
        pygame.joystick.init()

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            controller = pygame.joystick.Joystick(0)
            controller.init()
            print("Controller connected: ", controller.get_name())
        else:
            raise NoControllerDetected("No controller detected. Turn on xbox controller")

        return controller

    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server")

        return not returnCode

    def add_distance_warner(self, distanceWarner):
        self._distanceWarner = distanceWarner

    def add_car(self, car):
        self._car = car

    def add_camera(self, camera):
        self._camera = camera
        self._camera.start_preview()

    def add_servo(self, servo):
        self._servo = servo

class X11ForwardingError(Exception):
    pass

class NoControllerDetected(Exception):
    pass