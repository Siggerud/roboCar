# Robocar
This is a project where I've built
a vehicle that can be controlled with a wireless xbox controller via bluetooth.

## Prerequisites

### Pairing you XBox controller
Pair your xBox One controller to your raspberry pi according to this [tutorial](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).

### Setting up remote connection
1. Enable your VNC connection by first opening the configuration settings
```
sudo raspi config
```
Enable Interface options -> VNC Enable

2. Find your ip adress for your raspberry pi
```
ifconfig
```
Look under wlan0 and find the adress after inet.

3. Download and install [RealVnc](https://www.realvnc.com/en/connect/download/combined/) for your OS.
Use the ip adress you found earlier to connect to your raspberry pi. Your pi needs to
be on the same network as the station you are connecting to it remotely from.

### Downloading necessary libraries
Due to some versions of libraries that might not work
correctly together when installed through pip, we need to use
sudo apt for some of the libraries instead 

```
sudo apt install -y libcamera-apps libcamera-dev libatlas-base-dev python3-kms++ python3-libcamera python3-pyqt5 python3-prctl
sudo apt install -y libhdf5-dev libhdf5-103 libjpeg-dev libjasper-dev

pip3 install picamera2
pip3 install pygame
pip3 install opencv-python
pip3 install pyserial
```

### Setting up pigpio







