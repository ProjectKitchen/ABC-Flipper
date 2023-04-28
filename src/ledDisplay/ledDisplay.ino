//Pin connected to latch pin (ST_CP) of 74HC595
const int latchPin = 12;
//Pin connected to clock pin (SH_CP) of 74HC595
const int clockPin = 11;
////Pin connected to Data in (DS) of 74HC595
const int dataPin = 13;

byte Tab[]={0xc0,0xf9,0xa4,0xb0,0x99,0x92,0x82,0xf8,0x80,0x90,0xff};

void setup() {
  //set pins to output because they are addressed in the main loop
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  Serial.begin(115200);
  Serial.println("reset");
}

void loop() {
  if (Serial.available() > 0) {
    // ASCII '0' through '9' characters are
    // represented by the values 48 through 57.
    // so if the user types a number from 0 through 9 in ASCII,
    // you can subtract 48 to get the actual value:
  int bitToSet = Serial.read() - 48;
  // write to the shift register with the correct bit set high:
  digitalWrite(latchPin, LOW);
  // shift the bits out:
  shiftOut(dataPin, clockPin, MSBFIRST, Tab[bitToSet]);
    // turn on the output so the LEDs can light up:
  digitalWrite(latchPin, HIGH);
  }
}
