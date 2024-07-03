import RPi.GPIO as GPIO
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide" # disable pygame welcome message
import pygame

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

		self._moveCar = False

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

		self._servoSet = False
		self._pwmServo = None
		self._lastServoStickValue = 0
		self._servoValueChanged = False
		self._servoPwmValue = 0
		self._pwmMinServo = 12.7
		self._pwmMaxServo = 1.4
		self._moveServo = False

	def handle_xbox_input(self, event, controller):
		eventType = event.type
		if eventType == pygame.JOYHATMOTION:
			self._prepare_car_for_turning(controller)
			self._moveCar = True
			self._moveServo = False
		elif eventType == pygame.JOYAXISMOTION:
			axis = event.axis
			if axis == 4 or axis == 5:
				self._prepare_car_for_throttle(controller, axis)
				self._moveCar = True
				self._moveServo = False
			elif axis == 2:
				self._prepare_for_servo_movement(controller)
				self._moveCar = False
				self._moveServo = True

		if self._moveCar:
			self._move_car()
		elif self._moveServo:
			self._move_servo()

	def add_servo(self, servoPin):
		self._servoSet = True

		GPIO.setup(servoPin, GPIO.OUT)
		self._pwmServo = GPIO.PWM(servoPin, 50)
		self._pwmServo.start(0)


	def _convert_button_press_to_pwm_value(self, pressValue, pwmMinValue, pwmMaxValue, valuePrecision):
		buttonMinValue = -1
		buttonMaxValue = 1

		pwmSpan = pwmMaxValue - pwmMinValue
		buttonSpan = buttonMaxValue - buttonMinValue

		valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)
		valueMapped = round(pwmMinValue + (valueScaled * pwmSpan), valuePrecision)

		return valueMapped

	def _prepare_car_for_turning(self, controller):
		turnValue = controller.get_hat(0)[0] # only handle the horizontal value
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

	def _prepare_for_servo_movement(self, controller):
		buttonPressValue = controller.get_axis(2)
		stickValue = round(buttonPressValue, 1)

		if stickValue == self._lastServoStickValue:
			self._servoValueChanged = False
		else:
			self._servoValueChanged = True
			self._servoPwmValue = self._convert_button_press_to_pwm_value(stickValue, self._pwmMinServo, self._pwmMaxServo, 1)
			self._lastServoStickValue = stickValue

	def _move_servo(self):
		if self._servoValueChanged:
			self._change_duty_cycle([self._pwmServo], self._servoPwmValue)

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

	def _prepare_car_for_throttle(self, controller, axis):
		buttonPressValue = controller.get_axis(axis)

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

	def cleanup(self):
		GPIO.cleanup()
		self._pwmA.stop()
		self._pwmB.stop()

		if self._servoSet:
			self._pwmServo.stop()