import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess

class XboxControl:
    def __init__(self):
        self._car = None
        self._camera = None

        self._x11Connected = self._check_if_X11_connected()
        if not self._x11Connected:
            return

        self._controller = self._set_controller()

    def start_controller(self, threadEvent):
        while not threadEvent.is_set():
            for event in pygame.event.get():
                if self._car:
                    self._car.handle_xbox_input(event, self._controller)
                if self._camera:
                    self._camera.handle_xbox_input(event, self._controller)

        self._car.cleanup()
        self._camera.cleanup()


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

    def add_car(self, car):
        self._car = car

    def add_camera(self, camera):
        self._camera = camera
        self._camera.start_preview()