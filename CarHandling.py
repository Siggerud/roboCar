import RPi.GPIO as GPIO
from roboCarHelper import scale_button_press_value

class CarHandling:
	def __init__(self, leftBackward, leftForward, rightBackward, rightForward, enA, enB):
		self._leftBackward = leftBackward
		self._leftForward = leftForward
		self._rightBackward = rightBackward
		self._rightForward = rightForward
		self._enA = enA
		self._enB = enB

		self._pwmTreshold = 30
		self._pwmMinTT = 0
		self._pwmMaxTT = 70

		self._turnLeft = False
		self._turnRight = False

		self._goForward = False
		self._goReverse = False

		self._gpioThrottle = {True: GPIO.HIGH, False: GPIO.LOW}

		GPIO.setup(leftBackward, GPIO.OUT)
		GPIO.setup(leftForward, GPIO.OUT)
		GPIO.setup(rightBackward, GPIO.OUT)
		GPIO.setup(rightForward, GPIO.OUT)
		GPIO.setup(enA, GPIO.OUT)
		GPIO.setup(enB, GPIO.OUT)

		self._pwmA = GPIO.PWM(enA, 100)
		self._pwmB = GPIO.PWM(enB, 100)

		self._pwmA.start(0)
		self._pwmB.start(0)

		self._turnButtons = [
			"D-PAD left",
			"D-PAD right",
			"D-PAD released"
		]

		self._gasAndReverseButtons = [
			"RT",
			"LT",
		]

	def handle_xbox_input(self, buttonAndPressValue):
		button, buttonPressValue = buttonAndPressValue
		if button in self._turnButtons:
			self._prepare_car_for_turning(button)
			self._move_car()
		elif button in self._gasAndReverseButtons:
			self._prepare_car_for_throttle(button, buttonPressValue)
			self._move_car()

	def _change_duty_cycle(self, pwms, speed):
		for pwm in pwms:
			pwm.ChangeDutyCycle(speed)

	def _adjust_gpio_values(self, gpioValues):
		leftForwardValue, rightForwardValue, leftBackwardValue, rightBackwardValue = gpioValues

		GPIO.output(self._leftForward, self._gpioThrottle[leftForwardValue])
		GPIO.output(self._rightForward, self._gpioThrottle[rightForwardValue])
		GPIO.output(self._leftBackward, self._gpioThrottle[leftBackwardValue])
		GPIO.output(self._rightBackward, self._gpioThrottle[rightBackwardValue])

	def _move_car(self):
		if self._goForward:
			if not self._turnLeft and not self._turnRight:
				gpioValues = [True, True, False, False]
			elif self._turnLeft:
				gpioValues = [False, True, False, False]
			elif self._turnRight:
				gpioValues = [True, False, False, False]
		elif self._goReverse:
			if not self._turnLeft and not self._turnRight:
				gpioValues = [False, False, True, True]
			elif self._turnLeft:
				gpioValues = [False, False, False, True]
			elif self._turnRight:
				gpioValues = [False, False, True, False]
		elif not self._goReverse and not self._goForward:
			if not self._turnLeft and not self._turnRight:
				gpioValues = [False, False, False, False]
			elif self._turnLeft:
				gpioValues = [False, True, True, False]
			elif self._turnRight:
				gpioValues = [True, False, False, True]

		self._adjust_gpio_values(gpioValues)


	def _prepare_car_for_turning(self, button):
		if button == "D-PAD left":
			self._turnLeft = True
			self._turnRight = False
		elif button == "D-PAD right":
			self._turnLeft = False
			self._turnRight = True
		elif button == "D-PAD released":
			self._turnLeft = False
			self._turnRight = False

		if not self._goForward and not self._goReverse:
			self._change_duty_cycle([self._pwmA, self._pwmB], self._pwmMaxTT)

	def _prepare_car_for_throttle(self, button, buttonPressValue):
		speed = scale_button_press_value(buttonPressValue, self._pwmMinTT, self._pwmMaxTT, 2)
		if speed > self._pwmTreshold: # only change speed if over the treshold
			self._change_duty_cycle([self._pwmA, self._pwmB], speed)
			if button == "RT":
				self._goForward = True
				self._goReverse = False
			elif button == "LT":
				self._goForward = False
				self._goReverse = True
		else:
			self._change_duty_cycle([self._pwmA, self._pwmB], 0)

			self._goForward = False
			self._goReverse = False

	def cleanup(self):
		GPIO.cleanup()
		self._pwmA.stop()
		self._pwmB.stop()
