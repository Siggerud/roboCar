from picamera2 import Picamera2, Preview
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
from libcamera import Transform
from time import sleep
import pygame

class Camera:
    def __init__(self, resolution, rotation=True):
        self._cam = Picamera2()

        if rotation:
            camera_config = self._cam.create_preview_configuration(main={"size": resolution}, transform=Transform(hflip=1, vflip=1))
        else:
            camera_config = self._cam.create_preview_configuration(main={"size": resolution})
        self._cam.configure(camera_config)

        self._controller = self._get_controller()
        if not self._controller:
            print("No controls found. Turn on the controller")
            return

    def start_preview(self, event):
        self._cam.start_preview(Preview.QT)  # must use this preview to run over ssh
        self._cam.start()  # start camera
        print("Starting camera preview")

        while not event.is_set():
            for event in pygame.event.get():
                eventType = event.type
                print(event)
        self._cam.close()

    def _get_controller(self):
        controller = None

        pygame.init()
        pygame.joystick.init()

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            controller = pygame.joystick.Joystick(0)
            controller.init()
            print("Controller connected: ", controller.get_name())

        return controller