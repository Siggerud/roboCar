import time
import socket
from picamera2 import Picamera2, MappedArray
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from libcamera import Transform

class Camera:
    def __init__(self, cameraHelper):
        self._picam = Picamera2()
        self._cameraHelper = cameraHelper
        self._set_up_picam()

        self._angleText = None
        self._speedText = None
        self._turnText = None
        self._zoomValue = 1.0
        self._hudActive = True

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

            self._picam.start_recording(self._encoder, output)

            self._read_control_values_for_video_feed(lock)

            with MappedArray(self._picam.create_overlay(self._config), 'main') as m:
                m.array[:50, :300] = [0, 0, 0, 255]  # Create a black rectangle for better visibility
                m.array[:50, :300] = [255, 255, 255, 255]  # Set the FPS text color (white)
                m.put_text(self._angleText, 10, 10, scale=3, color=[255, 255, 255, 255])  # Position at (10, 10)

    def cleanup(self):
        self._picam.stop_recording()

    def _read_control_values_for_video_feed(self, lock):
        with lock:
            self._angleText = self._cameraHelper.get_angle_text()
            self._speedText = self._cameraHelper.get_speed_text()
            self._turnText = self._cameraHelper.get_turn_text()
            self._zoomValue = self._cameraHelper.get_zoom_value()
            self._hudActive = self._cameraHelper.get_hud_value()

