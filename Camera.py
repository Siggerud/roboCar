from picamera2 import Picamera2, Preview, MappedArray
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from libcamera import Transform
import time
import cv2
from time import sleep # TODO: remove when finished testing
from roboCarHelper import map_value_to_new_scale

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

		# text on video properties
		self._colour = (0, 255, 0)
		self._origin = (10, 250)
		self._font = cv2.FONT_HERSHEY_SIMPLEX
		self._scale = 1
		self._thickness = 1

		# control values displayed on camera feed
		self._currentServoAngle = "0"

	def start_preview(self):
		self._cam.pre_callback = self._apply_timestamp # callback for video feed
		self._cam.start_preview(Preview.QT)  # must use this preview to run over ssh or VNC
		self._cam.start(show_preview=True)  # start camera

		self._standardSize = self._cam.capture_metadata()['ScalerCrop'][2:]
		self._full_res = self._cam.camera_properties['PixelArraySize']

		print("Starting camera preview")

		sleep(2)

	def handle_xbox_input(self, buttonAndValue):
		button, buttonPressValue = buttonAndValue
		if button in self._zoomButtons:
			self._prepare_for_zooming(buttonPressValue)

			if self._zoomCamera:
				self._zoom()

	def set_current_servo_angle(self, currentServoAngle):
		self._currentServoAngle = str(currentServoAngle)


	def cleanup(self):
		self._cam.close()

	def _apply_timestamp(self, request):
		angleText = "Angle: " + self._currentServoAngle + "\nyes"
		with MappedArray(request, "main") as m:
			cv2.putText(m.array, angleText, self._origin, self._font, self._scale, self._colour, self._thickness)

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
			self._zoomValue = map_value_to_new_scale(stickValue, self._minZoomValue, self._maxZoomValue, 2,
													 self._zoomButtonMinValue, self._zoomButtonMaxValue)
			self._lastStickValue = stickValue
		else:
			self._zoomCamera = False

	def _check_if_button_press_within_valid_range(self, buttonPressValue):
		if buttonPressValue >= self._zoomButtonMaxValue and buttonPressValue <= self._zoomButtonMinValue:
			return True
		return False