from picamera2 import Picamera2, Preview, MappedArray
import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "3" #disable info and warning logging
from libcamera import Transform
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
		self._zoomValue = 1
		self._zoomCamera = False

		self._zoomButtonMinValue = 0
		self._zoomButtonMaxValue = -1

		self._zoomButtons = [
			"LSB vertical"
		]

		# text on video properties
		self._colour = (0, 255, 0)
		self._origins = [(10, 270), (10, 240), (10, 210), (10, 180)]
		self._font = cv2.FONT_HERSHEY_SIMPLEX
		self._scale = 1
		self._thickness = 1

		self._car = None
		self._servo = None

	def start_preview(self):
		self._cam.pre_callback = self._insert_control_values_on_video_feed # callback for video feed
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

	def cleanup(self):
		self._cam.close()

	def add_car(self, car):
		self._car = car

	def add_servo(self, servo):
		self._servo = servo

	def _insert_control_values_on_video_feed(self, request):
		with MappedArray(request, "main") as m:
			originCounter = 0

			zoomText = "Zoom: " + self._get_zoom_value_in_x_form() + "x"
			cv2.putText(m.array, zoomText, self._get_origin(originCounter), self._font, self._scale, self._colour,
						self._thickness)
			originCounter += 1

			if self._servo:
				angleText = "Angle: " + self._servo.get_current_servo_angle()
				cv2.putText(m.array, angleText, self._get_origin(originCounter), self._font, self._scale, self._colour, self._thickness)
				originCounter += 1

			if self._car:
				speedText = "Speed: " + self._car.get_current_speed() + "%"
				cv2.putText(m.array, speedText, self._get_origin(originCounter), self._font, self._scale, self._colour, self._thickness)
				originCounter += 1

				turnText = "Turn: " + self._car.get_current_turn_value()
				cv2.putText(m.array, turnText, self._get_origin(originCounter), self._font, self._scale, self._colour,
							self._thickness)
				originCounter += 1

	def _get_zoom_value_in_x_form(self):
		return str(round((1 / self._zoomValue), 2))

	def _get_origin(self, count):
		return self._origins[count]

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