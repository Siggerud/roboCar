import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess
from threading import Thread
from time import time

class XboxControl:
    def __init__(self):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._controller = self._set_controller()

        self._car = None
        self._servo = None
        self._distanceWarner = None

        self._cameraEnabled = False
        self._cameraHelper = None

        self._threads = []
        self._threadLock = None

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

        self._pushButtons = {
            0: "A",
            1: "B",
            3: "X",
            4: "Y",
            6: "LB",
            7: "RB",
            11: "Start",
            15: "Back"
        }

        self._pushButtonsStates = self._create_push_button_states_dict()

        self._exitButton = "Start"

        # keeps track of last time exit button was pushed
        self._exitButtonLastPush = None

    def add_distance_warner(self, distanceWarner):
        self._distanceWarner = distanceWarner

    def add_car(self, car):
        self._car = car

    def enable_camera(self, cameraHelper, lock):
        self._cameraEnabled = True
        self._cameraHelper = cameraHelper
        self._threadLock = lock

    def add_servo(self, servo):
        self._servo = servo

    def activate_distance_warner(self, event):
        thread = Thread(target=self._listen_for_distance_warnings, args=(event,))
        self._threads.append(thread)
        thread.start()

    def activate_car_controlling(self, event):
        if self._cameraEnabled:
            thread = Thread(target=self._start_controller, args=(event, self._threadLock))
        else:
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

        if self._distanceWarner:
            self._distanceWarner.cleanup()

    def _start_controller(self, threadEvent, lock=None):
        self._print_button_explanation()

        while not threadEvent.is_set():
            for event in pygame.event.get():
                buttonAndPressValue = self._get_button_and_press_value_from_event(event)
                if self._check_for_exit_event(buttonAndPressValue):
                    self._exit_program(threadEvent)
                    break

                if self._car:
                    self._car.handle_xbox_input(buttonAndPressValue)
                if self._servo:
                    self._servo.handle_xbox_input(buttonAndPressValue)
                if self._cameraEnabled:
                    self._cameraHelper.handle_xbox_input(buttonAndPressValue)
                    self._cameraHelper.update_control_values_for_video_feed(lock)

    def _print_button_explanation(self):
        print()
        print("Controller layout: ")
        if self._car:
            print("Car controls:")
            print("Turn left: " + self._car.car_buttons()["Left"])
            print("Turn right: " + self._car.car_buttons()["Right"])
            print("Drive forward: " + self._car.car_buttons()["Gas"])
            print("Reverse: " + self._car.car_buttons()["Reverse"])
            print()
        if self._servo:
            print("Servo controls:")
            print("Turn servo: " + self._servo.servo_buttons()["Servo"])
            print()
        if self._cameraEnabled:
            print("Camera controls")
            print("Zoom camera: " + self._cameraHelper.camera_buttons()["Zoom"])

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
        elif eventType == pygame.JOYBUTTONDOWN or eventType == pygame.JOYBUTTONUP:
            button = self._get_pushed_button()

        return (button, buttonPressValue)

    def _exit_program(self, threadEvent):
        threadEvent.set()
        print("Exiting program...")

    def _check_for_exit_event(self, buttonAndPressValue):
        button, pressValue = buttonAndPressValue
        if button == self._exitButton:
            # check if exit button has been pushed
            if self._pushButtonsStates[self._exitButton] == 1:

                # check how long ago it was pushed
                if self._exitButtonLastPush:
                    if (time() - self._exitButtonLastPush) < 0.5:
                        return True
                    else:
                        self._exitButtonLastPush = time()
                else:
                    self._exitButtonLastPush = time()

        return False

    def _create_push_button_states_dict(self):
        pushedButtonStates = {}
        for num in list(self._pushButtons.values()):
            pushedButtonStates[num] = 0

        return pushedButtonStates

    def _get_pushed_button(self):
        for num in list(self._pushButtons.keys()):
            button = self._pushButtons[num]
            if self._controller.get_button(num) != self._pushButtonsStates[button]:
                self._pushButtonsStates[button] = self._controller.get_button(num)

                return button

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


class X11ForwardingError(Exception):
    pass

class NoControllerDetected(Exception):
    pass