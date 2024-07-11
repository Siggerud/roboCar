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
        self._serialConnection.write(b"back\n")

    def _activate_front_distance_sensor(self):
        print("Activating front distance sensor...")
        self._serialConnection.write(b"front\n")

    def listen_for_incoming_sensor_data(self):
        if self._connection.in_waiting > 0:
            serialReading = self._serialConnection.readline().decode('utf-8').rstrip()
            side, distance = serialReading.trim().split()
            print(f"Side {side}, distance {distance}")

        self._connection.close()

    def cleanup(self):
        GPIO.cleanup()


