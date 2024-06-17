from CarHandling import CarHandling
import RPi.GPIO as GPIO
from threading import Thread, Event

GPIO.setmode(GPIO.BOARD)

# define GPIO pins
leftBackward = 16
leftForward = 15
rightBackward = 22
rightForward = 18
enA = 11
enB = 13

def handle_car():
    handler = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
    handler.handle_xbox_input(event)

myEvent = Event()
thread1 = Thread(target=handle_car, args=(myEvent,))
thread1.start()
