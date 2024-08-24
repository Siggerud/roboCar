from picamera2 import Picamera2
from flask import Response
import io

class Camera:
    def __init__(self):
        self._picam = Picamera2()
        self._start_camera()

    def _start_camera(self):
        config = self._picam.create_still_configuration(main={"size": (640, 480)})
        self._picam.configure(config)
        self._picam.start()


    def _generate_frames(self):
        stream = io.BytesIO()

        while True:
            stream.seek(0)
            self._picam.capture_file(stream, format='jpeg')
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + stream.getvalue() + b'\r\n'
            stream.seek(0)
            stream.truncate()

    def video_feed(self):
        return Response(self._generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')