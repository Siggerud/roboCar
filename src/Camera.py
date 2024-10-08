import cv2
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from picamera2 import Picamera2
from time import time

class Camera:
    def __init__(self, resolution, cameraHelper, rotation=True):
        self._dispW, self._dispH = resolution
        self._centerX = int(self._dispW / 2)
        self._centerY = int(self._dispH / 2)
        self._cameraHelper = cameraHelper
        self._rotation = rotation

        self._picam2 = Picamera2()
        self._picam2.preview_configuration.main.size = resolution
        self._picam2.preview_configuration.main.format = "RGB888"
        self._picam2.preview_configuration.align()
        self._picam2.configure("preview")
        self._picam2.start()

        # text on video properties
        self._colour = (0, 255, 0)
        self._textPositions = self._set_text_positions()
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._scale = 1
        self._thickness = 1

        self._angleText = None
        self._speedText = None
        self._turnText = None
        self._zoomValue = 1.0
        self._hudActive = True

        self._fps = 0
        self._weightPrevFps = 0.9
        self._weightNewFps = 0.1
        self._fpsPos = (10, 30)

    def show_camera_feed(self):
        tStart = time() # start timer for calculating fps

        # get raw image
        im = self._picam2.capture_array()

        # rotate/flip image
        if self._rotation:
            im = self._rotate_image(im)

        # read control values from external classes
        self._read_control_values_for_video_feed()

        # resize image when zooming
        if self._zoomValue != 1.0:
            im = self._get_zoomed_image(im)

        # add control values to cam feed
        if self._hudActive:
            self._add_text_to_cam_feed(im)

        cv2.imshow("Camera", im)
        cv2.waitKey(1)

        # calculate fps
        self._calculate_fps(tStart)

    def cleanup(self):
        cv2.destroyAllWindows()
        self._picam2.close()

    def _set_text_positions(self):
        spacingVertical = 30

        horizontalCoord = 10
        verticalCoord = self._dispH - 15

        positions = []
        for i in range(4):
            position = (horizontalCoord, verticalCoord - i * spacingVertical)
            positions.append(position)

        return positions

    def _calculate_fps(self, startTime):
        endTime = time()
        loopTime = endTime - startTime

        self._fps = self._weightPrevFps * self._fps + self._weightNewFps * (1 / loopTime)

    def _rotate_image(self, image):
        return cv2.flip(image, -1)

    def _get_zoomed_image(self, image):
        halfZoomDisplayWidth = int(self._dispW / (2 * self._zoomValue))
        halfZoomDisplayHeight = int(self._dispH / (2 * self._zoomValue))

        regionOfInterest = image[self._centerY - halfZoomDisplayHeight:self._centerY + halfZoomDisplayHeight,
                           self._centerX - halfZoomDisplayWidth:self._centerX + halfZoomDisplayWidth]

        im = cv2.resize(regionOfInterest, (self._dispW, self._dispH), cv2.INTER_LINEAR)

        return im

    def _add_text_to_cam_feed(self, image):
        # add control values to camera feed
        counter = 0
        cv2.putText(image, "Zoom: " + str(self._zoomValue) + "x", self._get_origin(counter), self._font, self._scale,
                    self._colour,
                    self._thickness)
        counter += 1

        if self._angleText:
            cv2.putText(image, self._angleText, self._get_origin(counter), self._font, self._scale, self._colour,
                        self._thickness)
            counter += 1

        if self._speedText:
            cv2.putText(image, self._speedText, self._get_origin(counter), self._font, self._scale, self._colour,
                        self._thickness)
            counter += 1

        if self._turnText:
            cv2.putText(image, self._turnText, self._get_origin(counter), self._font, self._scale, self._colour,
                        self._thickness)
            counter += 1

        # display fps
        cv2.putText(image, self._get_fps(), self._fpsPos, self._font, self._scale, self._colour,
                    self._thickness)

    def _get_fps(self):
        return str(int(self._fps)) + " FPS"

    def _read_control_values_for_video_feed(self):
        self._angleText = self._cameraHelper.get_angle_text()
        self._speedText = self._cameraHelper.get_speed_text()
        self._turnText = self._cameraHelper.get_turn_text()
        self._zoomValue = self._cameraHelper.get_zoom_value()
        self._hudActive = self._cameraHelper.get_hud_value()

    def _get_origin(self, count):
        return self._textPositions[count]