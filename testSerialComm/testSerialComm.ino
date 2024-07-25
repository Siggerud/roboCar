//variables for back sensor
boolean sendDistanceBack = false;
int inputPin1 = A0; // define ultrasonic receive pin (Echo)
int outputPin1 = A1; // define ultrasonic send pin(Trig)

//variables for front sensor
boolean sendDistanceFront = false;
int inputPin2 = A2; // define ultrasonic receive pin (Echo)
int outputPin2 = A3; // define ultrasonic send pin(Trig)

long baudrate = 115200; // the highest speed a pi can communicate with an arduino

void setup() {
  //set pin modes
  pinMode(inputPin1, INPUT);
  pinMode(outputPin1, OUTPUT);

  pinMode(inputPin2, INPUT);
  pinMode(outputPin2, OUTPUT);

  //start serial communication
  Serial.begin(baudrate);
}

void loop() {
  //listen for incoming commands from pi
  listen_for_commands();

  // write sensor values to pi
  if (sendDistanceBack) {
    write_to_serial(inputPin1, outputPin1);
  } else if (sendDistanceFront) {
    write_to_serial(inputPin2, outputPin2);
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
