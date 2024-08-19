import subprocess
from threading import Thread
from xboxControl import XboxControl

class CarControl:
    def __init__(self):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._xboxControl = XboxControl()

        self._car = None
        self._servo = None
        self._arduinoCommunicator = None

        self._cameraEnabled = False
        self._cameraHelper = None

        self._threads = []
        self._threadLock = None

    def add_arduino_communicator(self, arduinoCommunicator):
        self._arduinoCommunicator = arduinoCommunicator

    def add_car(self, car):
        self._car = car

    def enable_camera(self, cameraHelper, lock):
        self._cameraEnabled = True
        self._cameraHelper = cameraHelper
        self._threadLock = lock

    def add_servo(self, servo):
        self._servo = servo

    def activate_arduino_communication(self, event):
        thread = Thread(target=self._listen_for_arduino_communication, args=(event,))
        self._threads.append(thread)
        thread.start()

    def activate_car_controlling(self, event):
        if self._cameraEnabled:
            thread = Thread(target=self._start_controller, args=(event, self._threadLock))
        else:
            thread = Thread(target=self._start_controller, args=(event,))
        self._threads.append(thread)
        thread.start()

    def cleanup(self):
        # close all threads
        for thread in self._threads:
            thread.join()

        if self._car:
            self._car.cleanup()

        if self._servo:
            self._servo.cleanup()

        if self._arduinoCommunicator:
            self._arduinoCommunicator.cleanup()

    def _start_controller(self, threadEvent, lock=None):
        self._print_button_explanation()

        while not threadEvent.is_set():
            for event in self._xboxControl.get_controller_events():
                buttonAndPressValue = self._xboxControl.get_button_and_press_value_from_event(event)
                if self._xboxControl.check_for_exit_event(buttonAndPressValue):
                    self._exit_program(threadEvent)
                    break

                if self._car:
                    self._car.handle_xbox_input(buttonAndPressValue)
                if self._servo:
                    self._servo.handle_xbox_input(buttonAndPressValue)
                if self._cameraEnabled:
                    self._cameraHelper.handle_xbox_input(buttonAndPressValue, lock)
                    self._cameraHelper.update_control_values_for_video_feed(lock)

    def _print_button_explanation(self):
        print()
        print("Controller layout: ")
        if self._car:
            print("Car controls:")
            print("Turn left: " + self._car.car_buttons()["Left"])
            print("Turn right: " + self._car.car_buttons()["Right"])
            print("Drive forward: " + self._car.car_buttons()["Gas"])
            print("Reverse: " + self._car.car_buttons()["Reverse"])
            print()
        if self._servo:
            print("Servo controls:")
            print("Turn servo: " + self._servo.servo_buttons()["Servo"])
            print()
        if self._cameraEnabled:
            print("Camera controls")
            print("Zoom camera: " + self._cameraHelper.camera_buttons()["Zoom"])
            print("Turn HUD on or off: " + self._cameraHelper.camera_buttons()["HUD"])
            print()

        print(f"Double tap {self._xboxControl.get_exit_button()} to exit")

    def _listen_for_arduino_communication(self, threadEvent):
        while not threadEvent.is_set():
            self._arduinoCommunicator.start()


    def _exit_program(self, threadEvent):
        threadEvent.set()
        print("Exiting program...")

    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server")

        return not returnCode


class X11ForwardingError(Exception):
    pass

