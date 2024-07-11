from CarHandling import CarHandling
from SerialCommunicator import SerialCommunicator
from DistanceWarner import DistanceWarner
from Camera import Camera
from ServoHandling import ServoHandling
from xboxControl import XboxControl
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
servoPin = 26 # BCM
buzzerPin = 29

car = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
servo = ServoHandling(servoPin)

resolution = (384, 288)
camera = Camera(resolution)

port = '/dev/ttyACM0'
baudrate = 9600
serialObj = SerialCommunicator(port, baudrate)  # serial connection to USB port

distanceWarner = DistanceWarner(buzzerPin, serialObj)

def handle_car(event):
    xboxControl = XboxControl()
    xboxControl.add_car(car)
    xboxControl.add_servo(servo)
    xboxControl.add_camera(camera)
    xboxControl.add_distance_warner(distanceWarner)

    xboxControl.start_controller(event)


myEvent = Event()
thread1 = Thread(target=handle_car, args=(myEvent,))
thread1.start()


try:
    while not myEvent.is_set(): # listen for any threads setting the event
        sleep(0.5)
except KeyboardInterrupt:
    myEvent.set()
    thread1.join()
    thread2.join()



