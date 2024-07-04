int inputPin = A0; // define ultrasonic receive pin (Echo)
int outputPin = A1; // define ultrasonic send pin(Trig)

void setup() {
  //start serial at baud rate 9600
  pinMode(inputPin, INPUT);
  pinMode(outputPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(outputPin, LOW); //send no signal
  delayMicroseconds(2); // wait 2 microseconds
  digitalWrite(outputPin, HIGH); //send signal for 10 microseconds
  delayMicroseconds(10); 
  digitalWrite(outputPin, LOW); //turn off signal
  float distance = pulseIn(inputPin, HIGH); //get distance by listening for signal
  distance= distance/5.8/10;

  Serial.println("Distance: " + String(distance)); //sending data
  delay(1000); // waiting for one second

}
