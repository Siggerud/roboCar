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
    if not parser["Components.enabled"]["Camera"]:
        return None

    cameraSpecs = parser["Camera.specs"]

    resolutionWidth = cameraSpecs.getint("ResolutionWidth")
    resolutionHeight = cameraSpecs.getint("ResolutionHeight")

    resolution = (resolutionWidth, resolutionHeight)
    camera = Camera(resolution, cameraHelper)

    return camera


def setup_arduino_communicator(parser):
    if not parser["Components.enabled"]["ArduinoCommunicator"]:
        return None

    arduinoCommunicatorData = parser["Arduino.specs"]

    port = arduinoCommunicatorData.get("Port")
    baudrate = arduinoCommunicatorData.getint("Baudrate", 9600)

    try:
        arduinoCommunicator = ArduinoCommunicator(port, baudrate)
    except InvalidPortError as e:
        print_startup_error(e)
        exit()

    buzzerPin = parser["Distance.buzzer.pin"].getint("Buzzer")

    if parser["Components.enabled"]["DistanceBuzzer"]:
        arduinoCommunicator.activate_distance_sensors(buzzerPin)

    if parser["Components.enabled"]["ProgressiveLights"]:
        progressiveLightPins = []
        lightPins = parser["Progressive.light.pins"]
        for key in lightPins:
            progressiveLightPins.append(lightPins.getint(key))

        arduinoCommunicator.activate_photocell_lights(progressiveLightPins)

    return arduinoCommunicator


def setup_servo(parser, plane):
    if plane == "horizontal":
        if not parser["Components.enabled"]["ServoHorizontal"]:
            return None
    elif plane == "vertical":
        if not parser["Components.enabled"]["ServoVertical"]:
            return None

    servoData = parser[f"Servo.handling.specs.{plane}"]

    servoPin = servoData.getint("ServoPin")
    minAngle = servoData.getint("MinAngle", -90)
    maxAngle = servoData.getint("MaxAngle", 90)

    servoPin = servoPin
    servoPin = convert_from_board_number_to_bcm_number(servoPin)

    servo = ServoHandling(
        servoPin,
        plane,
        minAngle,
        maxAngle
    )

    return servo


def setup_car(parser):
    print(parser.sections())
    if not parser["Components.enabled"].getboolean("CarHandling"):
        return None

    carHandlingPins = parser["Car.handling.pins"]

    # define GPIO pins
    rightForward = carHandlingPins.getint("RightForward")  # IN2
    rightBackward = carHandlingPins.getint("RightBackward")  # IN1
    leftForward = carHandlingPins.getint("LeftForward")  # IN4
    leftBackward = carHandlingPins.getint("LeftBackward")  # IN3
    enA = carHandlingPins.getint("EnA")
    enB = carHandlingPins.getint("EnB")

    # define car handling
    car = CarHandling(
        rightForward,
        rightBackward,
        leftForward,
        leftBackward,
        enA,
        enB
    )

    return car


# set up parser to read input values
parser = ConfigParser()
parser.read("config.ini")

# set GPIO layout
GPIO.setmode(GPIO.BOARD)

# set up car controller
try:
    carController = CarControl()
except (X11ForwardingError, NoControllerDetected) as e:
    print_startup_error(e)
    exit()

car = setup_car(parser)

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







