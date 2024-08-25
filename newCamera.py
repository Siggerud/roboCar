import time
import socket
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

class Camera:
    def __init__(self):
        self._picam = Picamera2()
        self._set_up_picam()

    def _set_up_picam(self):
        self._picam.configure(self._picam.create_video_configuration())
        self._encoder = H264Encoder(10000000)

    def start_video_feed(self, event):
        while not event.is_set():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("0.0.0.0", 9999))
                sock.listen()
                conn, addr = sock.accept()
                stream = conn.makefile("wb")
                output = FileOutput(stream)

                self._picam.start_recording(self._encoder, output)
                time.sleep(9999)

    def cleanup(self):
        self._picam.stop_recording()

