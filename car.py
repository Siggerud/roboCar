from CarHandling import CarHandling
from SerialCommunicator import SerialCommunicator
from Camera import Camera
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
servoPin = 37

def handle_car(event):
    handler = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
    handler.add_servo(servoPin)
    handler.handle_xbox_input(event)

def get_serial_data(event):
    serialObj = SerialCommunicator('/dev/ttyACM0', 9600)  # serial connection to USB port
    serialObj.open_communication(event)

def start_camera(event):
    resolution = (384, 288)
    camera = Camera(resolution)
    camera.start_preview(event)

myEvent = Event()
#thread1 = Thread(target=handle_car, args=(myEvent,))
#thread1.start()

#thread2 = Thread(target=get_serial_data, args=(myEvent,))
#thread2.start()

thread3 = Thread(target=start_camera, args=(myEvent,))
thread3.start()

try:
    while not myEvent.is_set(): # listen for any threads setting the event
        sleep(0.5)
except KeyboardInterrupt:
    myEvent.set()
    #thread1.join()
    #thread2.join()
    thread3.join()


