import RPi.GPIO as GPIO
import pygame

class CarHandling:
    def __init__(self, leftBackward, leftForward, rightBackward, rightForward, enA, enB):
        self._leftBackward = leftBackward
        self._leftForward = leftForward
        self._rightBackward = rightBackward
        self._rightForward = rightForward
        self._enA = enA
        self._enB = enB

        self._pwmTreshold = 30
        self._latestTurnDirection = "straight"
        self._lastDirection = "forward"

        self._goForward = False
        self._goReverse = False


        GPIO.setup(leftBackward, GPIO.OUT)
        GPIO.setup(leftForward, GPIO.OUT)
        GPIO.setup(rightBackward, GPIO.OUT)
        GPIO.setup(rightForward, GPIO.OUT)
        GPIO.setup(enA, GPIO.OUT)
        GPIO.setup(enB, GPIO.OUT)

        self._pwmA = GPIO.PWM(enA, 100)
        self._pwmB = GPIO.PWM(enB, 100)

        self._pwmA.start(0)
        self._pwmB.start(0)

        self._controller = self._get_controller()

    def _get_controller(self):
        pygame.init()
        pygame.joystick.init()

        num_joysticks = pygame.joystick.get_count()
        if num_joysticks > 0:
            controller = pygame.joystick.Joystick(0)
            controller.init()
            print("Controller connected: ", controller.get_name())
        else:
            print("No controls found")

        return controller

    def _convert_button_press_to_speed(self, pressValue):
        buttonMinValue = -1
        buttonMaxValue = 1
        pwmMinValue = 0
        pwmMaxValue = 70

        pwmSpan = pwmMaxValue - pwmMinValue
        buttonSpan = buttonMaxValue - buttonMinValue

        valueScaled = float(pressValue - buttonMinValue) / float(buttonSpan)

        valueMapped = round(pwmMinValue + (valueScaled * pwmSpan), 2)

        return valueMapped

    def _handle_turn_values(self):
        turnValue = self._controller.get_hat(0)[0] # only handle the horizontal value
        if turnValue == -1:
            turnDirection = "left"
        elif turnValue == 1:
            turnDirection = "right"
        elif turnValue == 0:
            turnDirection = "straight"

        self._lastTurnDirection = turnDirection

    def _change_duty_cycle(self, speed):
        self._pwmA.ChangeDutyCycle(speed)
        self._pwmB.ChangeDutyCycle(speed)

    def _handle_axis_values(self, event):
        axis = event.axis
        print(axis)
        buttonPressValue = self._controller.get_axis(axis)

        if axis == 4:
            self._goForward = True
            self._goReverse = False
        elif axis == 5:
            self._goReverse = True
            self._goReverse = False
        else:
            self._change_duty_cycle(0)

            self._goReverse = False
            self._goForward = False


    def handle_xbox_input(self):
        try:
            while True:
                for event in pygame.event.get():
                    eventType = event.type

                    if eventType == pygame.JOYHATMOTION:
                        self._handle_turn_values()
                    elif eventType == pygame.JOYAXISMOTION:
                        self._handle_axis_values(event)

                    if self._goForward:
                        if self._latestTurnDirection == "straight":
                            print("drive")
                            GPIO.output(self._leftForward, GPIO.HIGH)
                            GPIO.output(self._rightForward, GPIO.HIGH)
                            GPIO.output(self._leftBackward, GPIO.LOW)
                            GPIO.output(self._rightBackward, GPIO.LOW)
                        elif self._latestTurnDirection == "left":
                            GPIO.output(self._leftForward, GPIO.LOW)
                            GPIO.output(self._rightForward, GPIO.HIGH)
                            GPIO.output(self._leftBackward, GPIO.LOW)
                            GPIO.output(self._rightBackward, GPIO.LOW)
                        elif self._latestTurnDirection == "right":
                            GPIO.output(self._leftForward, GPIO.HIGH)
                            GPIO.output(self._rightForward, GPIO.LOW)
                            GPIO.output(self._leftBackward, GPIO.LOW)
                            GPIO.output(self._rightBackward, GPIO.LOW)

                    elif self._goReverse:
                        if (self._latestTurnDirection== "straight"):
                            GPIO.output(self._leftForward, GPIO.LOW)
                            GPIO.output(self._rightForward, GPIO.LOW)
                            GPIO.output(self._leftBackward, GPIO.HIGH)
                            GPIO.output(self._rightBackward, GPIO.HIGH)
                        elif self._latestTurnDirection == "left":
                            GPIO.output(self._leftForward, GPIO.LOW)
                            GPIO.output(self._rightForward, GPIO.LOW)
                            GPIO.output(self._leftBackward, GPIO.LOW)
                            GPIO.output(self._rightBackward, GPIO.HIGH)
                        elif self._latestTurnDirection == "right":
                            GPIO.output(self._leftForward, GPIO.LOW)
                            GPIO.output(self._rightForward, GPIO.LOW)
                            GPIO.output(self._leftBackward, GPIO.HIGH)
                            GPIO.output(self._rightBackward, GPIO.LOW)

        except KeyboardInterrupt:
            print("Exiting")

        finally:
            GPIO.cleanup()
            self._pwmA.stop()
            self._pwmB.stop()
