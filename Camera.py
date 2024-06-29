from picamera2 import Picamera2, Preview
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from libcamera import Transform
from time import sleep

class Camera:
    def __init__(self, resolution, rotation=True):
        self._cam = Picamera2()

        if rotation:
            camera_config = self._cam.create_preview_configuration(main={"size": resolution}, transform=Transform(hflip=1, vflip=1))
        else:
            camera_config = self._cam.create_preview_configuration(main={"size": resolution})
        self._cam.configure(camera_config)

    def start_preview(self, event):
        self._cam.start_preview(Preview.QT)  # must use this preview to run over ssh
        self._cam.start()  # start camera
        print("Starting camera preview")

        while not event.is_set():
            sleep(0.5)
        self._cam.close()