from picamera2 import Picamera2
from flask import Response
import io
from PIL import Image, ImageDraw, ImageFont

class Camera:
    def __init__(self, resolution, cameraHelper, lock):
        self._picam = Picamera2()
        self._cameraHelper = cameraHelper
        self._lock = lock
        self._start_camera(resolution)

        self._font = ImageFont.load_default()

        self._angleText = None
        self._speedText = None
        self._turnText = None
        self._zoomValue = 1.0
        self._hudActive = True

    def _start_camera(self, resolution):
        config = self._picam.create_still_configuration(main={"size": resolution})
        self._picam.configure(config)
        self._picam.start()


    def _generate_frames(self):
        stream = io.BytesIO()

        while True:
            stream.seek(0)
            self._picam.capture_file(stream, format='jpeg')

            stream.seek(0)

            image = Image.open(stream)
            draw = ImageDraw.Draw(image)

            # Position for the number (bottom-right corner)
            text_position = (image.width - 100, image.height - 50)

            self._read_control_values_for_video_feed()

            # Draw the text on the image
            draw.text(text_position, self._speedText, font=self._font, fill=(255, 255, 255))

            # Save the modified image back to the stream
            stream = io.BytesIO()
            image.save(stream, format='jpeg')

            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + stream.getvalue() + b'\r\n'

            stream.seek(0)

            stream.truncate()

    def _read_control_values_for_video_feed(self):
        with self._lock:
            self._angleText = self._cameraHelper.get_angle_text()
            self._speedText = self._cameraHelper.get_speed_text()
            self._turnText = self._cameraHelper.get_turn_text()
            self._zoomValue = self._cameraHelper.get_zoom_value()
            self._hudActive = self._cameraHelper.get_hud_value()

    def video_feed(self):
        return Response(self._generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')