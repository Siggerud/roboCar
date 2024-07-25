//variables for back sensor
boolean sendDistanceBack = false;
int inputPinBack = A0; // define ultrasonic receive pin (Echo)
int outputPinBack = A1; // define ultrasonic send pin(Trig)

//variables for front sensor
boolean sendDistanceFront = false;
int inputPinFront = A2; // define ultrasonic receive pin (Echo)
int outputPinFront = A3; // define ultrasonic send pin(Trig)

long baudrate = 115200; // the highest speed a pi can communicate with an arduino

void setup() {
  //set pin modes
  pinMode(inputPinBack, INPUT);
  pinMode(outputPinBack, OUTPUT);

  pinMode(inputPinFront, INPUT);
  pinMode(outputPinFront, OUTPUT);

  //start serial communication
  Serial.begin(baudrate);
}

void loop() {
  //listen for incoming commands from pi
  listen_for_commands();

  // write sensor values to pi
  if (sendDistanceBack) {
    write_to_serial(inputPinBack, outputPinBack);
  } else if (sendDistanceFront) {
    write_to_serial(inputPinFront, outputPinFront);
  }

  //reset boolean values
  sendDistanceBack = false;
  sendDistanceFront = false;

}

void listen_for_commands() {
  if (Serial.available()){ // check if there is incoming data over the serial port
    String command = Serial.readStringUntil('\n'); //command from raspberry pi
    if (command == "back"){
      sendDistanceBack = true;
    } else if (command == "front"){
      sendDistanceFront = true;
    }
  }
}

void write_to_serial(int inputPin, int outputPin) {
  digitalWrite(outputPin, LOW); //send no signal
  delayMicroseconds(2); // wait 2 microseconds
  digitalWrite(outputPin, HIGH); //send signal for 10 microseconds
  delayMicroseconds(10); 
  digitalWrite(outputPin, LOW); //turn off signal
  float distance = pulseIn(inputPin, HIGH); //get distance by listening for signal
  distance= distance/5.8/10;

  Serial.println(String(distance)); //sending data
}
