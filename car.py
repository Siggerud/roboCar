import RPi.GPIO as GPIO
import time
import pygame

def convert_button_press_to_speed(pressValue):
	if pressValue > 0:
		output = round(pressValue, 2)
	else:
		output = 0

	return output

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

startTime = time.time()
while True:	
	if time.time() - startTime < 10:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.JOYAXISMOTION:
				speed = controller.get_axis(4)
				print(speed)
	else:
		break

pin1 = 16
pin2 = 18
pin3 = 22
pin4 = 15
enA = 11
enB = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)
GPIO.setup(pin3, GPIO.OUT)
GPIO.setup(pin4, GPIO.OUT)
GPIO.setup(enA, GPIO.OUT)
GPIO.setup(enB, GPIO.OUT)

pwmA = GPIO.PWM(enA, 100)
pwmB = GPIO.PWM(enB, 100)

pwmA.start(0)
pwmB.start(0)

try:
	while True:
		choise = input("Pick a number: ")
		percent = int(input("Pick speed percentage: "))
		
		if percent >= 0 and percent <= 100:
			pwmA.ChangeDutyCycle(percent)
			pwmB.ChangeDutyCycle(percent)

		if choise == "1":
			GPIO.output(pin1, GPIO.HIGH)
			sleep(1)
			GPIO.output(pin1, GPIO.LOW)
		elif choise == "2":
			GPIO.output(pin2, GPIO.HIGH)
			sleep(1)
			GPIO.output(pin2, GPIO.LOW)
		elif choise  == "3":
			GPIO.output(pin3, GPIO.HIGH)
			sleep(1)
			GPIO.output(pin3, GPIO.LOW)
		elif choise == "4":
			GPIO.output(pin4, GPIO.HIGH)
			sleep(1)
			GPIO.output(pin4, GPIO.LOW)
	
except KeyboardInterrupt:
	GPIO.cleanup()
	pwmA.stop()
	pwmB.stop()

finally:
	GPIO.cleanup()
	pwmA.stop()
	pwmB.stop()
