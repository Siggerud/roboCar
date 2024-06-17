from CarHandling import CarHandling
import RPi.GPIO as GPIO
from threading import Thread, Event
import time
import serial

GPIO.setmode(GPIO.BOARD)

# define GPIO pins
leftBackward = 16
leftForward = 15
rightBackward = 22
rightForward = 18
enA = 11
enB = 13

def handle_car(event):
    handler = CarHandling(leftBackward, leftForward, rightBackward, rightForward, enA, enB)
    handler.handle_xbox_input(event)

def get_serial_data(event):
    ser = serial.Serial('/dev/ttyACM0', 9600)  # serial connection to USB port
    time.sleep(2)

    try:
        while True:
            if event.is_set():
                break

            if ser.in_waiting > 0:
                print(ser.readline().decode('utf-8').rstrip())
    #except KeyboardInterrupt:
    #    print("Exiting")
    finally:
        ser.close()


myEvent = Event()
thread1 = Thread(target=handle_car, args=(myEvent,))
thread1.start()

thread2 = Thread(target=get_serial_data, args=(myEvent,))
thread2.start()

#time.sleep(5)
#myEvent.set()

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    myEvent.set()
    thread1.join()
    thread2.join()


