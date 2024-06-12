import RPi.GPIO as GPIO
import time
import pygame

leftBackward = 16
leftForward = 18
rightBackward = 22
rightForward = 15
enA = 11
enB = 13

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
	pwmMaxValue = 100

	buttonSpan = buttonMaxValue - buttonMinValue
	pwmSpan = pwmMaxValue - pwmMinValue

	valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)

	return pwmMinValue + (valueScaled * pwmMaxValue)

pygame.init()
pygame.joystick.init()

num_joysticks = pygame.joystick.get_count()

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
			if event.type == pygame.JOYAXISMOTION:
				buttonPressForward = controller.get_axis(4)
				buttonPressBackward = controller.get_axis(5)

				if buttonPressForward != -1:
					value = buttonPressForward
				elif buttonPressBackward != -1:
					value = buttonPressBackward
				speed = convert_button_press_to_speed(value)
				#print(speed)
				pwmA.ChangeDutyCycle(speed)
				pwmB.ChangeDutyCycle(speed)

				if buttonPressForward != -1:
					GPIO.output(leftForward, GPIO.HIGH)
					GPIO.output(rightForward, GPIO.HIGH)
					GPIO.output(leftBackward, GPIO.LOW)
					GPIO.output(rightBackward, GPIO.LOW)
				elif buttonPressBackward != -1:
					GPIO.output(leftForward, GPIO.LOW)
					GPIO.output(rightForward, GPIO.LOW)
					GPIO.output(leftBackward, GPIO.HIGH)
					GPIO.output(rightBackward, GPIO.HIGH)
except KeyboardInterrupt:
	print("Exiting")

finally:
	GPIO.cleanup()
	pwmA.stop()
	pwmB.stop()
