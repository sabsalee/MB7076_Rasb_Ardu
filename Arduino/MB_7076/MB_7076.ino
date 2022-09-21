const int anPin = 1;
long anVolt, cm, inches;

void setup (){
  Serial.begin(57600);
}

void read_sensor (){
anVolt = analogRead(anPin);
//Serial.println(anVolt);
cm = anVolt*2; //Takes bit count and converts it to mm
Serial.println(cm);
}

void loop () {
  read_sensor();
  delay(1000);
}
