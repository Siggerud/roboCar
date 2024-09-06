import subprocess
from multiprocessing import Process, Array, Value
from xboxControl import XboxControl
from time import sleep

class CarControl:
    def __init__(self):
        if not self._check_if_X11_connected():
            raise X11ForwardingError("X11 forwarding not detected.")

        self._xboxControl = XboxControl()

        self._car = None
        self._servoEnabled = False
        self._servos = []
        self._arduinoCommunicator = None

        self._camera = None
        self._cameraHelper = None

        self._processes = []

        self._buttonToObjectDict = {
        }

        self.shared_array = Array('d', (0.0, 0.0, 0.0, 0.0, 1.0))
        self.shared_flag = Value('b', False)

    def add_arduino_communicator(self, arduinoCommunicator):
        self._arduinoCommunicator = arduinoCommunicator

    def add_car(self, car):
        self._car = car

    def add_camera(self, camera):
        self._camera = camera

    def add_camera_helper(self, cameraHelper):
        self._cameraHelper = cameraHelper

    def add_servo(self, servo):
        self._servos.append(servo)
        if not self._servoEnabled:
            self._servoEnabled = True

    def activate_camera(self):
        process = Process(target=self._start_camera, args=(self.shared_array, self.shared_flag))
        self._processes.append(process)
        process.start()

    def activate_arduino_communication(self):
        process = Process(target=self._listen_for_arduino_communication, args=(self.shared_flag,))
        self._processes.append(process)
        process.start()

    def activate_car_handling(self):
        process = Process(target=self._start_car_handling, args=(self.shared_flag,))
        self._processes.append(process)
        process.start()

    def cleanup(self):
        # close all threads
        for process in self._processes:
            process.join()

    def _start_car_handling(self, flag):
        self._print_button_explanation()
        self._map_all_objects_to_buttons()

        self._car.setup()

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

                if self._cameraHelper:
                    self._cameraHelper.update_control_values_for_video_feed(self.shared_array)

        if self._car:
            self._car.cleanup()

        if self._servoEnabled:
            for servo in self._servos:
                servo.cleanup()

        print("Exiting car handling")

    def _start_camera(self, shared_array, flag):
        self._camera.setup()

        while not flag.value:
            self._camera.show_camera_feed(shared_array)

        self._camera.cleanup()

    def _listen_for_arduino_communication(self, flag):
        self._arduinoCommunicator.setup()

        while not flag.value:
            # start the communicator
            self._arduinoCommunicator.start()
            sleep(0.01)  # sleep too not use too much CPU resources

        # cleanup when flag is set to true
        self._arduinoCommunicator.cleanup()
        print("Exiting arduino")

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
        if self._servoEnabled:
            print("Servo controls:")
            for servo in self._servos:
                print("Turn servo" + servo.get_plane() + ": " + servo.servo_buttons()["Servo"])
            print()
        if self._camera:
            print("Camera controls")
            print("Zoom camera: " + self._cameraHelper.camera_buttons()["Zoom"])
            print("Turn HUD on or off: " + self._cameraHelper.camera_buttons()["HUD"])
            print()

        print(f"Double tap {self._xboxControl.get_exit_button()} to exit")

    def _map_all_objects_to_buttons(self):
        if self._car:
            self._add_object_to_buttons(self._car.car_buttons(), self._car)

        if self._servoEnabled:
            for servo in self._servos:
                self._add_object_to_buttons(servo.servo_buttons(), servo)

        if self._cameraHelper:
            self._add_object_to_buttons(self._cameraHelper.camera_buttons(), self._cameraHelper)

    def _add_object_to_buttons(self, buttonDict, roboObject):
        for button in list(buttonDict.values()):
            self._buttonToObjectDict[button] = roboObject

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

