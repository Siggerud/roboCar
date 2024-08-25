import time
import socket
from picamera2 import Picamera2, MappedArray
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from libcamera import Transform
import cv2

class Camera:
    def __init__(self, cameraHelper, lock):
        self._picam = Picamera2()
        self._cameraHelper = cameraHelper
        self._set_up_picam()
        self._lock = lock

        self._angleText = None
        self._speedText = None
        self._turnText = None
        self._zoomValue = 1.0
        self._hudActive = True

        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._scale = 1
        self._colour = (0, 255, 0)
        self._thickness = 1

    def apply_text(self, request):
        self._read_control_values_for_video_feed()
        with MappedArray(request, "main") as m:
            cv2.putText(m.array, self._angleText, (100, 100), self._font, self._scale, self._colour, self._thickness)


    def _set_up_picam(self):
        self._config = self._picam.create_video_configuration(transform=Transform(hflip=1, vflip=1))
        self._picam.configure(self._config) # flip the image
        self._encoder = H264Encoder(10000000)

    def start_video_feed(self, lock):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", 9999))
            sock.listen()
            conn, addr = sock.accept()
            stream = conn.makefile("wb")
            output = FileOutput(stream)
            self._picam.pre_callback = self.apply_text
            self._picam.start_recording(self._encoder, output)
            time.sleep(30)

    def cleanup(self):
        self._picam.stop_recording()

    def _read_control_values_for_video_feed(self):
        with self._lock:
            self._angleText = self._cameraHelper.get_angle_text()
            self._speedText = self._cameraHelper.get_speed_text()
            self._turnText = self._cameraHelper.get_turn_text()
            self._zoomValue = self._cameraHelper.get_zoom_value()
            self._hudActive = self._cameraHelper.get_hud_value()

