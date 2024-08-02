from CarHandling import CarHandling
from DistanceWarner import DistanceWarner, InvalidPortError
from Camera import Camera
from ServoHandling import ServoHandling
from xboxControl import XboxControl, x11ForwardingError
from roboCarHelper import print_startup_error
import RPi.GPIO as GPIO
from time import sleep
from threading import Event

# define GPIO pins
rightForward = 22 # IN2 
rightBackward = 18 # IN1
leftForward = 16 # IN4
leftBackward = 15 # IN3
enA = 11
enB = 13
servoPin = 26 # BCM
buzzerPin = 29

GPIO.setmode(GPIO.BOARD)

# define car handling
car = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)

# define servo aboard car
servo = ServoHandling(servoPin)

# define camera aboard car
resolution = (384, 288)
camera = Camera(resolution)

# define distance warning system for
port = '/dev/ttyACM0'
baudrate = 115200 # the highest communication rate between a pi and an arduino

try:
    distanceWarner = DistanceWarner(buzzerPin, port, baudrate)
except InvalidPortError as e:
    print_startup_error(e)
    exit()

# set up car controller

try:
    xboxControl = XboxControl()
except x11ForwardingError as e:
    print_startup_error(e)
    exit()

xboxControl.add_car(car)
xboxControl.add_servo(servo)
xboxControl.add_camera(camera)
xboxControl.add_distance_warner(distanceWarner)

# activate distance warning and car controlling
myEvent = Event()
xboxControl.activate_distance_warner(myEvent)
xboxControl.activate_car_controlling(myEvent)



# keep process running until keyboard interrupt
try:
    while not myEvent.is_set(): # listen for any threads setting the event
        sleep(0.5)
except KeyboardInterrupt:
    myEvent.set() # set event to stop all active processes
    xboxControl.cleanup() # cleanup to finish all threads and close processes
    GPIO.cleanup()



