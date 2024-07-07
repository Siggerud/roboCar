from CarHandling import CarHandling
from SerialCommunicator import SerialCommunicator
from Camera import Camera
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
servoPin = 37

car = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
car.add_servo(servoPin)

resolution = (384, 288)
camera = Camera(resolution)

def handle_car(event):
    xboxControl = XboxControl()
    xboxControl.add_car(car)
    xboxControl.add_camera(camera)
    xboxControl.start_controller(event)

def get_serial_data(event):
    serialObj = SerialCommunicator('/dev/ttyACM0', 9600)  # serial connection to USB port
    serialObj.activate_back_distance_sensor()
    serialObj.activate_front_distance_sensor()
    serialObj.listen_for_incoming_arduino_data(event)


myEvent = Event()
thread1 = Thread(target=handle_car, args=(myEvent,))
thread1.start()

thread2 = Thread(target=get_serial_data, args=(myEvent,))
thread2.start()

try:
    while not myEvent.is_set(): # listen for any threads setting the event
        sleep(0.5)
except KeyboardInterrupt:
    myEvent.set()
    thread1.join()
    thread2.join()



