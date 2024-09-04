from CarHandling import CarHandling
from ArduinoCommunicator import ArduinoCommunicator, InvalidPortError
from Camera import Camera
from CameraHelper import CameraHelper
from ServoHandling import ServoHandling
from carControl import CarControl, X11ForwardingError
from xboxControl import NoControllerDetected
from roboCarHelper import print_startup_error, convert_from_board_number_to_bcm_number
import RPi.GPIO as GPIO
from threading import Event
from configparser import ConfigParser

def setup_camera(parser, cameraHelper):
    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.get("ResolutionWidth")
    resolutionHeight = cameraSpecs.get("ResolutionHeight")

    if not resolutionWidth or not resolutionHeight:
        return None

    resolution = (int(resolutionWidth), int(resolutionHeight))
    camera = Camera(resolution, cameraHelper)

    return camera


def setup_arduino_communicator(parser):
    arduinoCommunicatorData = parser["Arduino.specs"]

    port = arduinoCommunicatorData.get("Port")
    baudrate = arduinoCommunicatorData.get("Baudrate", 9600)

    if not port:
        return None

    try:
        arduinoCommunicator = ArduinoCommunicator(port, int(baudrate))
    except InvalidPortError as e:
        print_startup_error(e)
        exit()

    buzzerPin = parser["Distance.buzzer.pin"].get("Buzzer")

    if buzzerPin:
        arduinoCommunicator.activate_distance_sensors(buzzerPin)

    progressiveLightPins = []
    lightPins = parser["Progressive.light.pins"]
    for key in lightPins:
        progressiveLightPins.append(int(lightPins[key]))

    if len(progressiveLightPins) != 0:
        arduinoCommunicator.activate_photocell_lights(progressiveLightPins)

    return arduinoCommunicator


def setup_servo(parser, plane):
    servoData = parser[f"Servo.handling.specs.{plane}"]

    servoPin = servoData.get("ServoPin")
    minAngle = servoData.get("MinAngle", -90)
    maxAngle = servoData("MaxAngle", 90)

    if not servoPin:
        return None

    servoPin = int(servoPin)
    servoPin = convert_from_board_number_to_bcm_number(servoPin)

    servo = ServoHandling(
        servoPin,
        plane,
        int(minAngle),
        int(maxAngle)
    )

    return servo


def setup_car(parser):
    carHandlingPins = parser["Car.handling.pins"]

    # define GPIO pins
    rightForward = carHandlingPins.get("RightForward")  # IN2
    rightBackward = carHandlingPins.get("RightBackward")  # IN1
    leftForward = carHandlingPins.get("LeftForward")  # IN4
    leftBackward = carHandlingPins.get("LeftBackward")  # IN3
    enA = carHandlingPins.get("EnA")
    enB = carHandlingPins.get("EnB")

    allPins = [
        rightForward,
        rightBackward,
        leftForward,
        leftBackward,
        enA,
        enB
    ]

    if None in allPins:
        return None

    allPins = [int(pin) for pin in allPins]

    # define car handling
    car = CarHandling(
        allPins[0],
        allPins[1],
        allPins[2],
        allPins[3],
        allPins[4],
        allPins[5]
    )

    return car


# set up parser to read input values
parser = ConfigParser()
parser.read("config.ini")

car = setup_car(parser)

# set GPIO layout
GPIO.setmode(GPIO.BOARD)

# set up car controller
try:
    carController = CarControl()
except (X11ForwardingError, NoControllerDetected) as e:
    print_startup_error(e)
    exit()

arduinoCommunicator = setup_arduino_communicator(parser)

# define servos aboard car
servoHorizontal = setup_servo(parser, "horizontal")
servoVertical = setup_servo(parser, "vertical")

cameraHelper = CameraHelper()
cameraHelper.add_car(car)
cameraHelper.add_servo(servoHorizontal)

camera = setup_camera(parser, cameraHelper)


# add components
carController.add_car(car)
carController.add_servo(servoHorizontal)
carController.add_servo(servoVertical)
carController.add_arduino_communicator(arduinoCommunicator)

# activate distance warning, camera and car controlling
myEvent = Event()
carController.enable_camera(cameraHelper)
carController.activate_arduino_communication(myEvent)
carController.activate_car_handling(myEvent)

# keep process running until keyboard interrupt
try:
    while not myEvent.is_set(): # listen for any threads setting the event
        # camera module will be run from main module, since cv2 is not thread safe
        camera.show_camera_feed()
except KeyboardInterrupt:
    myEvent.set() # set event to stop all active processes
finally:
    carController.cleanup() # cleanup to finish all threads and close processes
    camera.cleanup()
    GPIO.cleanup()







