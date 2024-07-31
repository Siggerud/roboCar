from picamera2 import Picamera2, Preview
import os
import cv2
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from libcamera import Transform
from time import sleep
from roboCarHelper import scale_button_press_value

class Camera:
	def __init__(self, resolution, rotation=True):
		self._cam = Picamera2()

		if rotation:
			camera_config = self._cam.create_preview_configuration(main={"size": resolution}, transform=Transform(hflip=1, vflip=1))
		else:
			camera_config = self._cam.create_preview_configuration(main={"size": resolution})
		self._cam.configure(camera_config)


		self._lastStickValue = 0
		self._minZoomValue = 1
		self._maxZoomValue = 0.35
		self._zoomValue = None
		self._zoomCamera = False

		self._zoomButtonMinValue = 0
		self._zoomButtonMaxValue = -1

		self._zoomButtons = [
			"LSB vertical"
		]

	def start_preview(self):
        self._cam.preview_configuration.main.format = "RGB888"
        self._cam.preview_configuration.align()
        self._cam.configure("preview")
		#self._cam.start_preview(Preview.QT)  # must use this preview to run over ssh
        self._cam.start()  # start camera

		self._standardSize = self._cam.capture_metadata()['ScalerCrop'][2:]
		self._full_res = self._cam.camera_properties['PixelArraySize']

		print("Starting camera preview")

		sleep(2)
		
		while True:
            frame = self._cam.capture_array()
            
            cv2.imshow("self._cam", frame)
            

	def handle_xbox_input(self, buttonAndValue):
		button, buttonPressValue = buttonAndValue
		if button in self._zoomButtons:
			self._prepare_for_zooming(buttonPressValue)

			if self._zoomCamera:
				self._zoom()


	def cleanup(self):
		self._cam.close()

	def _zoom(self):
		size = [int(s * self._zoomValue) for s in self._standardSize]
		offset = [(r - s) // 2 for r, s in zip(self._full_res, size)]
		self._cam.set_controls({"ScalerCrop": offset + size})

		self._cam.capture_metadata()  # this zooms in

	def _prepare_for_zooming(self, buttonPressValue):
		if self._check_if_button_press_within_valid_range(buttonPressValue):
			stickValue = round(buttonPressValue, 1)
		else:
			stickValue = self._zoomButtonMinValue

		if stickValue != self._lastStickValue:
			self._zoomCamera = True
			self._zoomValue = scale_button_press_value(stickValue, self._minZoomValue, self._maxZoomValue, 2,
													   self._zoomButtonMinValue, self._zoomButtonMaxValue)
			self._lastStickValue = stickValue
		else:
			self._zoomCamera = False

	def _check_if_button_press_within_valid_range(self, buttonPressValue):
		if buttonPressValue >= self._zoomButtonMaxValue and buttonPressValue <= self._zoomButtonMinValue:
			return True
		return False




