import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess

class XboxControl:
    def __init__(self):
        self._x11Connected = self._check_if_X11_connected()
        if not self._x11Connected:
            return

        self._controller = self._set_controller()

    def get_controller(self):
        return self._controller

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
