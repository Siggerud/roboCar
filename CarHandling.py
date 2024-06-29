import RPi.GPIO as GPIO
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame
import subprocess

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

		self._servoSet = False
		self._pwmServo = None
		self._lastServoStickValue = 0
		self._servoValueChanged = False
		self._pwmMinServo = 12.7
		self._pwmMaxServo = 1.4

		self._x11Connected = self._check_if_X11_connected()
		if not self._x11Connected:
			print("Unable to connect to forwarded X server. Start VcXSrc.")
			return

		self._controller = self._get_controller()
		if not self._controller:
			print("No controls found. Turn on the controller")
			return

	def handle_xbox_input(self, threadEvent):
		if not self._x11Connected:
			self._cleanup()
			return

		if not self._controller:
			self._cleanup()
			return

		while not threadEvent.is_set():

			for event in pygame.event.get():
				eventType = event.type

				if eventType == pygame.JOYHATMOTION:
					self._handle_turn_values()
				elif eventType == pygame.JOYAXISMOTION:
					axis = event.axis
					if axis == 4 or axis == 5:
						self._handle_axis_values(event, axis)
					elif axis == 2:
						self._handle_servo_values(event)

				if self._goForward:
					if not self._turnLeft and not self._turnRight:
						GPIO.output(self._leftForward, GPIO.HIGH)
						GPIO.output(self._rightForward, GPIO.HIGH)
						GPIO.output(self._leftBackward, GPIO.LOW)
						GPIO.output(self._rightBackward, GPIO.LOW)
					elif self._turnLeft:
						GPIO.output(self._leftForward, GPIO.LOW)
						GPIO.output(self._rightForward, GPIO.HIGH)
						GPIO.output(self._leftBackward, GPIO.LOW)
						GPIO.output(self._rightBackward, GPIO.LOW)
					elif self._turnRight:
						GPIO.output(self._leftForward, GPIO.HIGH)
						GPIO.output(self._rightForward, GPIO.LOW)
						GPIO.output(self._leftBackward, GPIO.LOW)
						GPIO.output(self._rightBackward, GPIO.LOW)

				elif self._goReverse:
					if not self._turnLeft and not self._turnRight:
						GPIO.output(self._leftForward, GPIO.LOW)
						GPIO.output(self._rightForward, GPIO.LOW)
						GPIO.output(self._leftBackward, GPIO.HIGH)
						GPIO.output(self._rightBackward, GPIO.HIGH)
					elif self._turnLeft:
						GPIO.output(self._leftForward, GPIO.LOW)
						GPIO.output(self._rightForward, GPIO.LOW)
						GPIO.output(self._leftBackward, GPIO.LOW)
						GPIO.output(self._rightBackward, GPIO.HIGH)
					elif self._turnRight:
						GPIO.output(self._leftForward, GPIO.LOW)
						GPIO.output(self._rightForward, GPIO.LOW)
						GPIO.output(self._leftBackward, GPIO.HIGH)
						GPIO.output(self._rightBackward, GPIO.LOW)
				elif not self._goReverse and not self._goForward:
					if not self._turnLeft and not self._turnRight:
						GPIO.output(self._leftForward, GPIO.LOW)
						GPIO.output(self._rightForward, GPIO.LOW)
						GPIO.output(self._leftBackward, GPIO.LOW)
						GPIO.output(self._rightBackward, GPIO.LOW)
					elif self._turnLeft:
						GPIO.output(self._leftForward, GPIO.LOW)
						GPIO.output(self._rightForward, GPIO.HIGH)
						GPIO.output(self._leftBackward, GPIO.HIGH)
						GPIO.output(self._rightBackward, GPIO.LOW)
					elif self._turnRight:
						GPIO.output(self._leftForward, GPIO.HIGH)
						GPIO.output(self._rightForward, GPIO.LOW)
						GPIO.output(self._leftBackward, GPIO.LOW)
						GPIO.output(self._rightBackward, GPIO.HIGH)

		self._cleanup()

	def add_servo(self, servoPin):
		self._servoSet = True

		GPIO.setup(servoPin, GPIO.OUT)
		self._pwmServo = GPIO.PWM(servoPin, 50)
		self._pwmServo.start(0)

	def _check_if_X11_connected(self):
		result = subprocess.run(["xset", "q"], capture_output = True, text = True)
		returnCode = result.returncode

		if not returnCode:
			print("Succesful connection to forwarded X11 server")

		return not returnCode

	def _get_controller(self):
		controller = None

		pygame.init()
		pygame.joystick.init()

		num_joysticks = pygame.joystick.get_count()
		if num_joysticks > 0:
			controller = pygame.joystick.Joystick(0)
			controller.init()
			print("Controller connected: ", controller.get_name())

		return controller

	def _convert_button_press_to_pwm_value(self, pressValue, pwmMinValue, pwmMaxValue, valuePrecision):
		buttonMinValue = -1
		buttonMaxValue = 1

		pwmSpan = pwmMaxValue - pwmMinValue
		buttonSpan = buttonMaxValue - buttonMinValue

		valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)
		valueMapped = round(pwmMinValue + (valueScaled * pwmSpan), valuePrecision)

		return valueMapped

	def _handle_turn_values(self):
		turnValue = self._controller.get_hat(0)[0] # only handle the horizontal value
		if turnValue == -1:
			self._turnLeft = True
			self._turnRight = False
		elif turnValue == 1:
			self._turnLeft = False
			self._turnRight = True
		elif turnValue == 0:
			self._turnLeft = False
			self._turnRight = False

		if not self._goForward and not self._goReverse:
			self._change_duty_cycle([self._pwmA, self._pwmB], self._pwmMaxTT)

	def _change_duty_cycle(self, pwms, speed):
		for pwm in pwms:
			pwm.ChangeDutyCycle(speed)

	def _handle_servo_values(self, event):
		buttonPressValue = self._controller.get_axis(2)
		stickValue = round(buttonPressValue, 1)

		if stickValue == self._lastServoStickValue:
			self._servoValueChanged = False
		else:
			self._servoValueChanged = True
			servoValue = self._convert_button_press_to_pwm_value(stickValue, self._pwmMinServo, self._pwmMaxServo, 1)
			self._change_duty_cycle([self._pwmServo], servoValue)

	def _handle_axis_values(self, event, axis):
		buttonPressValue = self._controller.get_axis(axis)

		speed = self._convert_button_press_to_pwm_value(buttonPressValue, self._pwmMinTT, self._pwmMaxTT, 2)
		if speed > self._pwmTreshold: # only change speed if over the treshold
			self._change_duty_cycle([self._pwmA, self._pwmB], speed)
			if axis == 4:
				self._goForward = True
				self._goReverse = False
			elif axis == 5:
				self._goForward = False
				self._goReverse = True
		else:
			self._change_duty_cycle([self._pwmA, self._pwmB], 0)

			self._goForward = False
			self._goReverse = False

	def _cleanup(self):
		GPIO.cleanup()
		self._pwmA.stop()
		self._pwmB.stop()

		if self._servoSet:
			self._pwmServo.stop()