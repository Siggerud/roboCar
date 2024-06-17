from CarHandling import CarHandling
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

# define GPIO pins
leftBackward = 16
leftForward = 15
rightBackward = 22
rightForward = 18
enA = 11
enB = 13

handler = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
handler.handle_xbox_input()
