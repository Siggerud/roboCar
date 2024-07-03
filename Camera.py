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
            camera_config = self._cam.create_preview_configuration(main={"size": resolution},
                                                                   transform=Transform(hflip=1, vflip=1))
        else:
            camera_config = self._cam.create_preview_configuration(main={"size": resolution})
        self._cam.configure(camera_config)

        self._lastStickValue = 0
        self._stickValueChanged = False
        self._minZoomValue = 1
        self._maxZoomValue = 0.35
        self._standardSize = None
        self._full_res = None

        self._controller = self._get_controller()
        if not self._controller:
            print("No controls found. Turn on the controller")
            return

    def start_preview(self, threadEvent):
        self._cam.start_preview(Preview.QT)  # must use this preview to run over ssh
        self._cam.start()  # start camera
        print("Starting camera preview")

        self._standardSize = self._cam.capture_metadata()['ScalerCrop'][2:]
        self._full_res = self._cam.camera_properties['PixelArraySize']

        while not threadEvent.is_set():
            for event in pygame.event.get():
                eventType = event.type

                if eventType == pygame.JOYAXISMOTION:
                    axis = event.axis
                    if axis == 1:
                        buttonPressValue = self._controller.get_axis(axis)
                        print(buttonPressValue)
                        if buttonPressValue >= -1 and buttonPressValue <= 0:
                            stickValue = self._round_nearest(buttonPressValue, 0.05)

                            if stickValue == self._lastStickValue:
                                self._stickValueChanged = False
                            else:
                                self._stickValueChanged = True
                                self._zoomValue = self._convert_button_press_to_pwm_value(stickValue,
                                                                                          self._minZoomValue,
                                                                                          self._maxZoomValue, 2)

                                self._lastServoStickValue = stickValue

            if self._stickValueChanged:
                #print(self._zoomValue)
                self._zoom()

        self._cam.close()

    def _zoom(self):
        size = [int(s * self._zoomValue) for s in self._standardSize]
        offset = [(r - s) // 2 for r, s in zip(self._full_res, size)]
        self._cam.set_controls({"ScalerCrop": offset + size})

        self._cam.capture_metadata()  # zooms in

    def _round_nearest(self, x, a):
        return round(x / a) * a

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

    def _convert_button_press_to_pwm_value(self, pressValue, pwmMinValue, pwmMaxValue, valuePrecision):
        buttonMinValue = -1
        buttonMaxValue = 1

        pwmSpan = pwmMaxValue - pwmMinValue
        buttonSpan = buttonMaxValue - buttonMinValue

        valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)
        valueMapped = round(pwmMinValue + (valueScaled * pwmSpan), valuePrecision)

        return valueMapped