import RPi.GPIO as GPIO

class DistanceWarner:
    def __init__(self, buzzerPin, serialConnection, frontSensor = True, backSensor = True):
        GPIO.setup(buzzerPin, GPIO.OUT)
        self._serialConnection = serialConnection
        self._distanceTreshold = 5

        if frontSensor:
            self._activate_front_distance_sensor()

        if backSensor:
            self._activate_back_distance_sensor()

    def _activate_back_distance_sensor(self):
        print("Activating back distance sensor...")
        command = b"back\n"
        self._serialConnection.send_command(command)

    def _activate_front_distance_sensor(self):
        print("Activating front distance sensor...")
        command = b"front\n"
        self._serialConnection.send_command(command)


    def listen_for_incoming_sensor_data(self):
        serialReading = self._serialConnection.read_incoming_data()
        if serialReading:
            print(serialReading)

    def cleanup(self):
        GPIO.cleanup()
        self._serialConnection.cleanup()


