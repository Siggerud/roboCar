from CarHandling import CarHandling
from DistanceWarner import DistanceWarner
from Camera import Camera
from ServoHandling import ServoHandling
from xboxControl import XboxControl
import RPi.GPIO as GPIO
from threading import Thread, Event
from time import sleep

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
baudrate = 115200 # the highest communication rate between a pi and an arduino

distanceWarner = DistanceWarner(buzzerPin, port, baudrate, buzzerPin)

xboxControl = XboxControl()
xboxControl.add_car(car)
xboxControl.add_servo(servo)
xboxControl.add_camera(camera)
xboxControl.add_distance_warner(distanceWarner)

def handle_car(event):
    xboxControl.start_controller(event)

def start_serial_comm(event):
    xboxControl.start_serial_comm(event)


myEvent = Event()
thread1 = Thread(target=handle_car, args=(myEvent,))
thread1.start()

thread2 = Thread(target=start_serial_comm, args=(myEvent,))
thread2.start()


try:
    while not myEvent.is_set(): # listen for any threads setting the event
        sleep(0.5)
except KeyboardInterrupt:
    myEvent.set()
    thread1.join()
    thread2.join()



