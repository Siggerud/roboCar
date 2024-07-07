//variables for back sensor
boolean sendDistanceBack = false;
int inputPin1 = A0; // define ultrasonic receive pin (Echo)
int outputPin1 = A1; // define ultrasonic send pin(Trig)

//variables for front sensor
boolean sendDistanceFront = false;
int inputPin2 = A2; // define ultrasonic receive pin (Echo)
int outputPin2 = A3; // define ultrasonic send pin(Trig)

void setup() {
  //start serial at baud rate 9600
  pinMode(inputPin1, INPUT);
  pinMode(outputPin1, OUTPUT);

  pinMode(inputPin2, INPUT);
  pinMode(outputPin2, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (sendDistanceBack && sendDistanceFront) {
    write_to_serial(inputPin1, outputPin1, "back");
    write_to_serial(inputPin2, outputPin2, "front");
  } else {
    if (sendDistanceBack) {
      write_to_serial(inputPin1, outputPin1, "back");
    } else if (sendDistanceFront) {
      write_to_serial(inputPin2, outputPin2, "front");
    }

    //if either of the distance sensors are not yet active, then check for serial data coming from raspberry pi
    listen_for_commands();
  }  

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

void write_to_serial(int inputPin, int outputPin, String direction) {
  digitalWrite(outputPin, LOW); //send no signal
  delayMicroseconds(2); // wait 2 microseconds
  digitalWrite(outputPin, HIGH); //send signal for 10 microseconds
  delayMicroseconds(10); 
  digitalWrite(outputPin, LOW); //turn off signal
  float distance = pulseIn(inputPin, HIGH); //get distance by listening for signal
  distance= distance/5.8/10;

  Serial.println(direction + " distance: " + String(distance)); //sending data

  delay(1000); // waiting for one second
}
