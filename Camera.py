import cv2
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from picamera2 import Picamera2
from time import time

class Camera:
    def __init__(self, resolution, cameraHelper, rotation = True):
        self._dispW, self._dispH = resolution
        self._centerX = int(self._dispW)
        self._centerY = int(self._dispH)
        self._cameraHelper = cameraHelper

        self._picam2 = Picamera2()
        self._picam2.preview_configuration.main.size = resolution
        self._picam2.preview_configuration.main.format = "RGB888"
        self._picam2.preview_configuration.align()
        self._picam2.configure("preview")
        self._picam2.start()

        # text on video properties
        self._colour = (0, 255, 0)
        # TODO: base origins on input resolution
        self._origins = [(10, 270), (10, 240), (10, 210), (10, 180)]
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._scale = 1
        self._thickness = 1

        self._angleText = None
        self._speedText = None
        self._turnText = None
        self._zoomValue = 1.0

        self._fps = 0
        self._fpsPos = (10, 30)

    def show_camera_feed(self, lock):
        tStart = time() # start timer for calculating fps

        im = self._picam2.capture_array()
        self._read_control_values_for_video_feed(lock)

        if self._zoomValue != 1.0:
            halfZoomDisplayWidth = int(self._dispW / (2 * self._zoomValue))
            halfZoomDisplayHeight = int(self._dispH / (2 * self._zoomValue))

            regionOfInterest = im[self._centerY - halfZoomDisplayHeight:self._centerY + halfZoomDisplayHeight,
                               self._centerX - halfZoomDisplayWidth:self._centerY + halfZoomDisplayWidth]

            im = cv2.resize(regionOfInterest, (self._dispW, self._dispH), cv2.INTER_LINEAR)

        # add control values to camera feed
        originCounter = 0
        if self._angleText:
            cv2.putText(im, self._angleText, self._get_origin(originCounter), self._font, self._scale, self._colour,
                        self._thickness)
            originCounter += 1

        if self._speedText:
            cv2.putText(im, self._speedText, self._get_origin(originCounter), self._font, self._scale, self._colour,
                        self._thickness)
            originCounter += 1

        if self._turnText:
            cv2.putText(im, self._turnText, self._get_origin(originCounter), self._font, self._scale, self._colour,
                        self._thickness)
            originCounter += 1

        # display fps
        cv2.putText(im, self._get_fps(), self._fpsPos, self._font, self._scale, self._colour,
                    self._thickness)

        cv2.imshow("Camera", im)
        cv2.waitKey(1)

        # calculate fps
        tEnd = time()
        loopTime = tEnd - tStart
        self._fps = 0.9 * self._fps + 0.1 * (1 / loopTime)

    def cleanup(self):
        cv2.destroyAllWindows()
        self._picam2.close()

    def _get_fps(self):
        return str(int(self._fps)) + " FPS"

    def _read_control_values_for_video_feed(self, lock):
        with lock:
            self._angleText = self._cameraHelper.get_angle_text()
            self._speedText = self._cameraHelper.get_speed_text()
            self._turnText = self._cameraHelper.get_turn_text()
            self._zoomValue = self._cameraHelper.get_zoom_value()

    def _get_origin(self, count):
        return self._origins[count]

"""
picam2 = Picamera2()
dispW=1280
dispH=720
picam2.preview_configuration.main.size = (dispW,dispH)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate=30
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
fps=0
pos=(30,60)
font=cv2.FONT_HERSHEY_SIMPLEX
height=1.5
weight=3
myColor=(0,0,255)
while True:
    tStart=time.time()
    im= picam2.capture_array()
    cv2.putText(im,str(int(fps))+' FPS',pos,font,height,myColor,weight)
    cv2.imshow("Camera", im)
    if cv2.waitKey(1)==ord('q'):
        break
    tEnd=time.time()
    loopTime=tEnd-tStart
    fps=.9*fps + .1*(1/loopTime)
cv2.destroyAllWindows()
"""