import RPi.GPIO as GPIO
import time
import pygame

# define GPIO pins
leftBackward = 16
leftForward = 18
rightBackward = 22
rightForward = 15
enA = 11
enB = 13

latestTurnValue = "straight"
latestForwardValue = -1.0
latestReverseValue = -1.0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(leftBackward, GPIO.OUT)
GPIO.setup(leftForward, GPIO.OUT)
GPIO.setup(rightBackward, GPIO.OUT)
GPIO.setup(rightForward, GPIO.OUT)
GPIO.setup(enA, GPIO.OUT)
GPIO.setup(enB, GPIO.OUT)

pwmA = GPIO.PWM(enA, 100)
pwmB = GPIO.PWM(enB, 100)

pwmA.start(0)
pwmB.start(0)

def convert_button_press_to_speed(pressValue):
	buttonMinValue = -1
	buttonMaxValue = 1
	pwmMinValue = 0
	pwmMaxValue = 70
	
	pwmSpan = pwmMaxValue - pwmMinValue
	buttonSpan = buttonMaxValue - buttonMinValue

	valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)
	
	valueMapped = round(pwmMinValue + (valueScaled * pwmSpan), 2)

	return valueMapped

pygame.init()
pygame.joystick.init()

num_joysticks = pygame.joystick.get_count()
print(num_joysticks)
if num_joysticks > 0:
	controller = pygame.joystick.Joystick(0)
	controller.init()
	print("Controller connected: ", controller.get_name())
else: 
	print("No controls found")
	exit(0)

try:
	while True:	
		for event in pygame.event.get():
			if event.type == pygame.JOYHATMOTION:
				turnValue = controller.get_hat(0)[0]
				if turnValue == -1:
					turnDirection = "left"
				elif turnValue == 1:
					turnDirection = "right"
				elif turnValue == 0:
					turnDirection = "straight"

				latestTurnValue = turnDirection

			elif event.type == pygame.JOYAXISMOTION:
				buttonPressForward = controller.get_axis(4)
				buttonPressBackward = controller.get_axis(5)
				print(event.axis)
				if buttonPressForward != -1.0:
					value = buttonPressForward
					latestForwardValue = value
				elif buttonPressBackward != -1.0:
					value = buttonPressBackward
					latestReverseValue = value
				speed = convert_button_press_to_speed(value)
				print(speed)
				pwmA.ChangeDutyCycle(speed)
				pwmB.ChangeDutyCycle(speed)



			if latestForwardValue != -1.0:
				if latestTurnValue == "straight":
					GPIO.output(leftForward, GPIO.HIGH)
					GPIO.output(rightForward, GPIO.HIGH)
					GPIO.output(leftBackward, GPIO.LOW)
					GPIO.output(rightBackward, GPIO.LOW)
				elif latestTurnValue == "left":
					GPIO.output(leftForward, GPIO.LOW)
					GPIO.output(rightForward, GPIO.HIGH)
					GPIO.output(leftBackward, GPIO.LOW)
					GPIO.output(rightBackward, GPIO.LOW)
				elif latestTurnValue == "right":
					GPIO.output(leftForward, GPIO.HIGH)
					GPIO.output(rightForward, GPIO.LOW)
					GPIO.output(leftBackward, GPIO.LOW)
					GPIO.output(rightBackward, GPIO.LOW)
			elif latestReverseValue != -1.0:
				if latestTurnValue == "straight":
					GPIO.output(leftForward, GPIO.LOW)
					GPIO.output(rightForward, GPIO.LOW)
					GPIO.output(leftBackward, GPIO.HIGH)
					GPIO.output(rightBackward, GPIO.HIGH)
				elif latestTurnValue == "left":
					GPIO.output(leftForward, GPIO.LOW)
					GPIO.output(rightForward, GPIO.LOW)
					GPIO.output(leftBackward, GPIO.LOW)
					GPIO.output(rightBackward, GPIO.HIGH)
				elif latestTurnValue == "right":
					GPIO.output(leftForward, GPIO.LOW)
					GPIO.output(rightForward, GPIO.LOW)
					GPIO.output(leftBackward, GPIO.HIGH)
					GPIO.output(rightBackward, GPIO.LOW)
			elif latestReverseValue == -1.0 and latestForwardValue == -1.0:
				pwmA.ChangeDutyCycle(100)
				pwmB.ChangeDutyCycle(100)

				if latestTurnValue == "left":
					GPIO.output(leftForward, GPIO.LOW)
					GPIO.output(rightForward, GPIO.HIGH)
					GPIO.output(leftBackward, GPIO.HIGH)
					GPIO.output(rightBackward, GPIO.LOW)
				elif latestTurnValue == "right":
					GPIO.output(leftForward, GPIO.HIGH)
					GPIO.output(rightForward, GPIO.LOW)
					GPIO.output(leftBackward, GPIO.LOW)
					GPIO.output(rightBackward, GPIO.HIGH)



except KeyboardInterrupt:
	print("Exiting")

finally:
	GPIO.cleanup()
	pwmA.stop()
	pwmB.stop()
