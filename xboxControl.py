import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess
from threading import Thread, Lock

class XboxControl:
    def __init__(self):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._controller = self._set_controller()

        self._car = None
        self._camera = None
        self._cameraHelper = None
        self._servo = None
        self._distanceWarner = None
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

    def add_distance_warner(self, distanceWarner):
        self._distanceWarner = distanceWarner

    def add_car(self, car):
        self._car = car

    def add_camera(self, camera, cameraHelper):
        self._camera = camera
        self._cameraHelper = cameraHelper
        self._threadLock = Lock()

    def add_servo(self, servo):
        self._servo = servo

    def activate_camera(self, event):
        thread = Thread(target=self._start_camera_feed, args=(event, self._threadLock))
        self._threads.append(thread)
        thread.start()

    def activate_distance_warner(self, event):
        thread = Thread(target=self._listen_for_distance_warnings, args=(event,))
        self._threads.append(thread)
        thread.start()

    def activate_car_controlling(self, event):
        if self._camera:
            thread = Thread(target=self._start_controller, args=(event,self._threadLock))
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

        if self._camera:
            self._camera.cleanup()

        if self._distanceWarner:
            self._distanceWarner.cleanup()

    def _start_camera_feed(self, threadEvent, lock):
        #while not threadEvent.is_set():
        self._camera.show_camera_feed()

    def _start_controller(self, threadEvent, lock=None):
        self._print_button_explanation()

        while not threadEvent.is_set():
            for event in pygame.event.get():
                buttonAndPressValue = self._get_button_and_press_value_from_event(event)
                if self._car:
                    self._car.handle_xbox_input(buttonAndPressValue)
                if self._servo:
                    self._servo.handle_xbox_input(buttonAndPressValue)
                if self._camera:
                    #self._cameraHelper.handle_xbox_input(buttonAndPressValue)
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
        if self._camera:
            print("Camera controls")
            # TODO: add method for this in either camera or camerahelper
            #print("Zoom camera: " + self._camera.camera_buttons()["Zoom"])

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


class X11ForwardingError(Exception):
    pass

class NoControllerDetected(Exception):
    pass