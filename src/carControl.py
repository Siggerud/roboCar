import subprocess
#from threading import Thread
from multiprocessing import Process, Array, Value
from xboxControl import XboxControl
from ArduinoCommunicator import ArduinoCommunicator
from Camera import Camera

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

        self._buttonToObjectDict = {
        }
        self.shared_dict = Array('d', (0.0, 0.0, 0.0, 0.0, 0.0))
        self.shared_flag = Value('b', False)

    def add_arduino_communicator(self, arduinoCommunicator):
        self._arduinoCommunicator = arduinoCommunicator

    def add_car(self, car):
        self._car = car

    def start_camera(self, resolution):
        thread = Process(target=self._start_camera, args=(self.shared_dict, self.shared_flag, resolution))
        self._threads.append(thread)
        thread.start()

    def enable_camera(self, cameraHelper):
        self._cameraEnabled = True
        self._cameraHelper = cameraHelper

    def _start_camera(self, shared_dict, shared_flag, resolution):
        camera = Camera(resolution)
        while not shared_flag.value:
            camera.show_camera_feed(shared_dict)

        camera.cleanup()

    def add_servo(self, servo):
        self._servo = servo

    def activate_arduino_communication(self):
        thread = Process(target=self._listen_for_arduino_communication, args=(self.shared_flag,))
        self._threads.append(thread)
        thread.start()

    def activate_car_handling(self):
        thread = Process(target=self._start_car_handling, args=(self.shared_flag,))
        self._threads.append(thread)
        thread.start()

    def cleanup(self):
        # close all threads
        for thread in self._threads:
            thread.join()

        #if self._car:
        #    self._car.cleanup()

        if self._servo:
            self._servo.cleanup()

        #if self._arduinoCommunicator:
        #    self._arduinoCommunicator.cleanup()

    def _start_car_handling(self, flag):
        self._print_button_explanation()
        self._map_all_objects_to_buttons()

        self._car.setup_gpio()

        while not flag.value:
            for event in self._xboxControl.get_controller_events():
                button, pressValue = self._xboxControl.get_button_and_press_value_from_event(event)
                if self._xboxControl.check_for_exit_event(button):
                    self._exit_program(flag)
                    break

                # get the object to take action based on the button pushed
                try:
                    self._buttonToObjectDict[button].handle_xbox_input(button, pressValue)
                except KeyError: # if key does not correspond to object, then go to next event
                    continue

                if self._cameraEnabled:
                    self._cameraHelper.update_control_values_for_video_feed(self.shared_dict)
        if self._car:
            self._car.cleanup()

        if self._servo:
            self._servo.cleanup()

        print("Exiting car handling")

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

    def _map_all_objects_to_buttons(self):
        if self._car:
            self._add_object_to_buttons(self._car.car_buttons(), self._car)

        if self._servo:
            self._add_object_to_buttons(self._servo.servo_buttons(), self._servo)

        if self._cameraEnabled:
            self._add_object_to_buttons(self._cameraHelper.camera_buttons(), self._cameraHelper)

    def _add_object_to_buttons(self, buttonDict, roboObject):
        for button in list(buttonDict.values()):
            self._buttonToObjectDict[button] = roboObject

    def _listen_for_arduino_communication(self, flag):
        self._arduinoCommunicator.start(flag)
        print("Exiting arduino")


    def _exit_program(self, flag):
        flag.value = True
        print("Exiting program...")

    def _check_if_X11_connected(self):
        result = subprocess.run(["xset", "q"], capture_output=True, text=True)
        returnCode = result.returncode

        if not returnCode:
            print("Succesful connection to forwarded X11 server")

        return not returnCode

class X11ForwardingError(Exception):
    pass

