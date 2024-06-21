from CarHandling import CarHandling
from SerialCommunicator import SerialCommunicator
import RPi.GPIO as GPIO
from threading import Thread, Event
from time import sleep

GPIO.setmode(GPIO.BOARD)

# define GPIO pins
leftBackward = 22 # IN2 
leftForward = 18 # IN1
rightBackward = 16 # IN4
rightForward = 15 # IN3
enA = 11
enB = 13

def handle_car(event):
    handler = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
    handler.handle_xbox_input(event)

def get_serial_data(event):
    serialObj = SerialCommunicator('/dev/ttyACM0', 9600)  # serial connection to USB port
    serialObj.open_communication(event)

myEvent = Event()
thread1 = Thread(target=handle_car, args=(myEvent,))
thread1.start()

thread2 = Thread(target=get_serial_data, args=(myEvent,))
thread2.start()


try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    myEvent.set()
    thread1.join()
    thread2.join()


