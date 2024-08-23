from CarHandling import CarHandling
from ArduinoCommunicator import ArduinoCommunicator, InvalidPortError
from Camera import Camera
from CameraHelper import CameraHelper
from ServoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from xboxControl import NoControllerDetected
from roboCarHelper import print_startup_error
import RPi.GPIO as GPIO
#from threading import Event, Lock
from multiprocessing import Event, Lock, Array

# define GPIO pins
rightForward = 22 # IN2 
rightBackward = 18 # IN1
leftForward = 16 # IN4
leftBackward = 15 # IN3
enA = 11
enB = 13

servoPin = 26 # BCM

buzzerPin = 29

lightPin1 = 36
lightPin2 = 31

# set GPIO layout
GPIO.setmode(GPIO.BOARD)

shared_dict = Array("i", {"angle": 0, "speed": 0, "turn": "", "zoom": 1.0})

# set up car controller
try:
    carController = CarControl()
except (X11ForwardingError, NoControllerDetected) as e:
    print_startup_error(e)
    exit()

# define distance warning system for car
port = '/dev/ttyACM0'
baudrate = 115200 # the highest communication rate between a pi and an arduino

try:
    arduinoCommunicator = ArduinoCommunicator(port, baudrate)
    arduinoCommunicator.activate_distance_sensors(buzzerPin)
    arduinoCommunicator.activate_photocell_lights([lightPin1, lightPin2])
except InvalidPortError as e:
    print_startup_error(e)
    exit()

# define car handling
car = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)

# define servo aboard car
servo = ServoHandling(servoPin)

# define camera aboard car
resolution = (384, 288)
cameraHelper = CameraHelper()
camera = Camera(resolution, shared_dict)
cameraHelper.add_car(car)
cameraHelper.add_servo(servo)
#cameraHelper.add_shared_data(shared_dict)

# add components
carController.add_car(car)
carController.add_servo(servo)
carController.add_arduino_communicator(arduinoCommunicator)

# activate distance warning, camera and car controlling
myEvent = Event()
lock = Lock()
carController.enable_camera(cameraHelper, lock)
carController.activate_arduino_communication(myEvent)
carController.activate_car_handling(myEvent)

# keep process running until keyboard interrupt
try:
    while not myEvent.is_set(): # listen for any threads setting the event
        # camera module will be run from main module, since cv2 is not thread safe
        camera.show_camera_feed(lock)
except KeyboardInterrupt:
    myEvent.set() # set event to stop all active processes
finally:
    carController.cleanup() # cleanup to finish all threads and close processes
    camera.cleanup()
    GPIO.cleanup()



